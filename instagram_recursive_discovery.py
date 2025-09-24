#!/usr/bin/env python3
"""
Instagram Recursive Discovery System - 5 LAYERS DEEP RECOMMENDED PAGES
🎯 Strategy: Start with seed pages → Find recommended → Find their recommended → 5 layers deep
🔍 Smart discovery: Follows recommendation chains recursively  
📊 Output: JSON file with all discovered profiles organized by layer
🚀 CLI Executable: python instagram_recursive_discovery.py <username1> <username2> ...
"""

import requests
import json
import sys
import time
import argparse
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ProfileData:
    username: str
    full_name: str
    followers: int
    following: int
    posts: int
    verified: bool
    private: bool
    profile_url: str
    discovery_layer: int
    discovered_from: str
    pk: str = ""

class InstagramRecursiveDiscovery:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
        }
        
        # Discovery tracking
        self.discovered_usernames: Set[str] = set()
        self.profiles_by_layer: Dict[int, List[ProfileData]] = {}
        self.total_api_calls = 0
        self.max_layers = 5
        self.max_recommended_per_user = 20
        
        # Initialize layers
        for i in range(self.max_layers + 1):
            self.profiles_by_layer[i] = []
    
    def discover_recursive(self, seed_usernames: List[str]) -> Dict[int, List[ProfileData]]:
        """
        Main recursive discovery method: Find recommended pages 5 layers deep
        """
        
        print(f"🚀 Starting Instagram Recursive Discovery - 5 LAYERS DEEP")
        print(f"🌱 Seed usernames: {', '.join(seed_usernames)}")
        print(f"🔍 Max layers: {self.max_layers}")
        print(f"📊 Max recommended per user: {self.max_recommended_per_user}")
        print("=" * 80)
        
        # Layer 0: Process seed usernames (skip profile details for now)
        current_layer_usernames = []
        for username in seed_usernames:
            if username not in self.discovered_usernames:
                # Create a basic profile for the seed without full details
                profile = ProfileData(
                    username=username,
                    full_name="",
                    followers=0,
                    following=0,
                    posts=0,
                    verified=False,
                    private=False,
                    profile_url=f"https://instagram.com/{username}",
                    discovery_layer=0,
                    discovered_from="seed"
                )
                self.profiles_by_layer[0].append(profile)
                current_layer_usernames.append(username)
                self.discovered_usernames.add(username)
                print(f"✅ Layer 0: Added seed @{username} (profile details skipped)")
        
        # Layers 1-5: Recursive discovery
        for layer in range(1, self.max_layers + 1):
            print(f"\n🔍 LAYER {layer}: Processing {len(current_layer_usernames)} profiles from layer {layer-1}")
            
            next_layer_usernames = []
            for username in current_layer_usernames:
                print(f"\n  🎯 Finding recommended for @{username} (Layer {layer-1} → {layer})")
                
                similar_accounts = self._get_similar_accounts(username)
                layer_count = 0
                
                for account in similar_accounts:
                    if account['username'] not in self.discovered_usernames:
                        profile = self._get_profile_details(account['username'])
                        
                        if profile:
                            profile.discovery_layer = layer
                            profile.discovered_from = username
                            self.profiles_by_layer[layer].append(profile)
                            next_layer_usernames.append(account['username'])
                            self.discovered_usernames.add(account['username'])
                            layer_count += 1
                            print(f"      ✅ Layer {layer}: @{account['username']} (from @{username})")
                        
                        # Small delay to avoid rate limiting
                        time.sleep(0.5)
                
                print(f"    📊 Found {layer_count} new profiles from @{username}")
                
                # Delay between users
                time.sleep(1)
            
            current_layer_usernames = next_layer_usernames
            
            total_layer = len(self.profiles_by_layer[layer])
            print(f"\n✅ LAYER {layer} COMPLETE: {total_layer} new profiles discovered")
            
            if not current_layer_usernames:
                print(f"🛑 No more profiles to process. Stopping at layer {layer}")
                break
        
        # Final summary
        self._print_discovery_summary()
        
        return self.profiles_by_layer
    
    def _get_profile_details(self, username: str) -> Optional[ProfileData]:
        """Get detailed profile information for a username"""
        
        url = f"{self.base_url}/ig_get_fb_profile_hover.php?username_or_url={username}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            self.total_api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'user_data' in data:
                    user_data = data['user_data']
                    
                    return ProfileData(
                        username=user_data.get('username', username),
                        full_name=user_data.get('full_name', ''),
                        followers=self._parse_follower_count(user_data.get('follower_count', 0)),
                        following=user_data.get('following_count', 0),
                        posts=user_data.get('media_count', 0),
                        verified=user_data.get('is_verified', False),
                        private=user_data.get('is_private', False),
                        profile_url=f"https://instagram.com/{username}",
                        discovery_layer=0,  # Will be set by caller
                        discovered_from="",  # Will be set by caller
                        pk=str(user_data.get('pk', ''))
                    )
            
            return None
            
        except requests.exceptions.RequestException:
            return None
    
    def _get_similar_accounts(self, username: str) -> List[Dict]:
        """Get similar accounts for a username"""
        
        url = f"{self.base_url}/get_ig_similar_accounts.php?username_or_url={username}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            self.total_api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    similar_accounts = []
                    for account in data:
                        if isinstance(account, dict) and account.get('username'):
                            similar_accounts.append({
                                'username': account['username'],
                                'full_name': account.get('full_name', ''),
                                'verified': account.get('is_verified', False)
                            })
                    return similar_accounts
                elif isinstance(data, dict) and 'error' not in data:
                    # Handle nested structure if needed
                    return []
            
            return []
            
        except requests.exceptions.RequestException:
            return []
    
    def _parse_follower_count(self, followers) -> int:
        """Parse follower count from various formats"""
        if isinstance(followers, int):
            return followers
        
        if isinstance(followers, str):
            # Remove commas and convert
            followers = followers.replace(',', '').replace(' ', '')
            
            # Handle K, M, B suffixes
            if followers.endswith('K'):
                return int(float(followers[:-1]) * 1000)
            elif followers.endswith('M'):
                return int(float(followers[:-1]) * 1000000)
            elif followers.endswith('B'):
                return int(float(followers[:-1]) * 1000000000)
            else:
                try:
                    return int(followers)
                except ValueError:
                    return 0
        
        return 0
    
    def _print_discovery_summary(self):
        """Print discovery summary statistics"""
        
        total_profiles = sum(len(profiles) for profiles in self.profiles_by_layer.values())
        
        print(f"\n{'='*80}")
        print(f"🎉 RECURSIVE DISCOVERY COMPLETE!")
        print(f"{'='*80}")
        print(f"📊 Total profiles discovered: {total_profiles}")
        print(f"🔧 Total API calls made: {self.total_api_calls}")
        
        # Layer breakdown
        print(f"\n📈 Discovery by Layer:")
        for layer in range(self.max_layers + 1):
            count = len(self.profiles_by_layer[layer])
            layer_name = "Seed" if layer == 0 else f"Layer {layer}"
            print(f"   {layer_name}: {count} profiles")
        
        # Top profiles by followers
        all_profiles = []
        for profiles in self.profiles_by_layer.values():
            all_profiles.extend(profiles)
        
        if all_profiles:
            all_profiles.sort(key=lambda x: x.followers, reverse=True)
            print(f"\n🏆 Top 10 Profiles by Followers:")
            for i, profile in enumerate(all_profiles[:10], 1):
                followers_str = self._format_number(profile.followers)
                verified_str = "✓" if profile.verified else ""
                print(f"   {i:2d}. @{profile.username} - {followers_str} followers {verified_str}")
    
    def _format_number(self, num: int) -> str:
        """Format numbers with K, M, B suffixes"""
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)
    
    def save_results(self, filename: str = None):
        """Save discovery results to JSON file"""
        
        if filename is None:
            timestamp = int(time.time())
            filename = f"instagram_recursive_discovery_{timestamp}.json"
        
        # Convert to serializable format
        results = {
            "discovery_summary": {
                "total_profiles": sum(len(profiles) for profiles in self.profiles_by_layer.values()),
                "total_api_calls": self.total_api_calls,
                "discovery_timestamp": datetime.now().isoformat(),
                "max_layers": self.max_layers
            },
            "profiles_by_layer": {}
        }
        
        for layer, profiles in self.profiles_by_layer.items():
            results["profiles_by_layer"][str(layer)] = [asdict(profile) for profile in profiles]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename

def main():
    parser = argparse.ArgumentParser(
        description="Instagram Recursive Discovery - Find recommended pages 5 layers deep",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python instagram_recursive_discovery.py nike adidas
  python instagram_recursive_discovery.py --key YOUR_API_KEY luxury ferrari
  python instagram_recursive_discovery.py --layers 3 --max-per-user 10 tesla
        """
    )
    
    parser.add_argument('usernames', nargs='+', 
                        help='Starting Instagram usernames (without @)')
    
    parser.add_argument('--key', '--api-key', 
                        default=None,
                        help='RapidAPI key (default: from INSTAGRAM_API_KEY env)')
    
    parser.add_argument('--layers', type=int, default=5,
                        help='Maximum discovery layers (default: 5)')
    
    parser.add_argument('--max-per-user', type=int, default=20,
                        help='Maximum recommended accounts per user (default: 20)')
    
    parser.add_argument('--output', '-o',
                        help='Output filename (default: auto-generated)')
    
    args = parser.parse_args()
    
    # Create discovery instance
    import os
    key = args.key or os.getenv('INSTAGRAM_API_KEY')
    if not key:
        print('❌ Missing INSTAGRAM_API_KEY environment variable (or pass --key)')
        sys.exit(1)
    discovery = InstagramRecursiveDiscovery(key)
    discovery.max_layers = args.layers
    discovery.max_recommended_per_user = args.max_per_user
    
    # Validate usernames
    clean_usernames = []
    for username in args.usernames:
        # Remove @ if present
        clean_username = username.lstrip('@')
        if clean_username:
            clean_usernames.append(clean_username)
    
    if not clean_usernames:
        print("❌ Error: No valid usernames provided")
        sys.exit(1)
    
    # Run discovery
    try:
        profiles_by_layer = discovery.discover_recursive(clean_usernames)
        
        # Save results
        output_file = discovery.save_results(args.output)
        
        print(f"\n🎯 Discovery complete! Check {output_file} for detailed results.")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Discovery interrupted by user")
        discovery.save_results("interrupted_" + (args.output or f"recursive_discovery_{int(time.time())}.json"))
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during discovery: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 