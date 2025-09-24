#!/usr/bin/env python3
"""
Instagram Ultimate Profile Scraper - COMPLETE DISCOVERY SYSTEM
✅ Hashtag search with pagination (2-3x more profiles!)
✅ Similar accounts discovery (find related profiles!)
✅ Full follower/following data for all profiles
"""

import requests
import json
import sys
import time
import re
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

class InstagramUltimateScraperr:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
        }
    
    def search_hashtag_with_pagination(self, hashtag: str, max_pages: int = 3) -> List[Dict]:
        """Search hashtag with pagination - WORKING PERFECTLY! 🎉"""
        
        clean_hashtag = hashtag.replace('#', '')
        print(f"🔍 Searching hashtag #{clean_hashtag} with pagination (up to {max_pages} pages)")
        
        all_users = {}
        pagination_token = None
        
        for page in range(max_pages):
            print(f"\n📄 Fetching hashtag page {page + 1}/{max_pages}")
            
            if pagination_token:
                url = f"{self.base_url}/search_hashtag.php?hashtag={clean_hashtag}&pagination_token={pagination_token}"
            else:
                url = f"{self.base_url}/search_hashtag.php?hashtag={clean_hashtag}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    page_users = self._extract_users_from_posts(data, f"hashtag page {page + 1}")
                    
                    for user in page_users:
                        username = user.get('username')
                        if username and username not in all_users:
                            all_users[username] = user
                    
                    pagination_token = data.get('pagination_token')
                    if not pagination_token:
                        print(f"✅ No more hashtag pages available")
                        break
                        
                    time.sleep(1)
                else:
                    print(f"❌ Hashtag page {page + 1} failed with status {response.status_code}")
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error on hashtag page {page + 1}: {e}")
                break
        
        print(f"✅ Hashtag search complete! Found {len(all_users)} unique users from hashtag")
        return list(all_users.values())
    
    def find_similar_accounts(self, usernames: List[str], max_similar_per_user: int = 5) -> List[Dict]:
        """Find similar accounts for given usernames - NEW DISCOVERY METHOD! 🚀"""
        
        print(f"\n🔍 Finding similar accounts for {len(usernames)} seed users")
        print(f"📊 Getting up to {max_similar_per_user} similar accounts per user")
        
        all_similar_users = {}
        
        for i, username in enumerate(usernames, 1):
            print(f"\n🎯 Finding similar accounts to @{username} ({i}/{len(usernames)})")
            
            url = f"{self.base_url}/get_ig_similar_accounts.php?username_or_url={username}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    similar_users = self._extract_similar_accounts(data, username, max_similar_per_user)
                    
                    for user in similar_users:
                        similar_username = user.get('username')
                        if similar_username and similar_username not in all_similar_users:
                            all_similar_users[similar_username] = user
                            print(f"      👤 Found similar: @{similar_username}")
                
                else:
                    print(f"❌ Similar accounts failed for @{username} (status {response.status_code})")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error for @{username}: {e}")
            
            # Small delay between requests
            time.sleep(1)
        
        print(f"\n✅ Similar accounts discovery complete! Found {len(all_similar_users)} additional users")
        return list(all_similar_users.values())
    
    def _extract_similar_accounts(self, data: Dict, seed_username: str, max_accounts: int) -> List[Dict]:
        """Extract similar account information from API response"""
        
        similar_users = []
        
        # Handle both dict (error case) and list (success case) responses
        if isinstance(data, dict):
            # Check if this is an error response
            if 'error' in data:
                print(f"      ❌ Error for @{seed_username}: {data.get('error', 'Unknown error')}")
                return []
            
            # If dict but no error, might be nested structure
            potential_lists = []
            if 'similar_accounts' in data:
                potential_lists.append(data['similar_accounts'])
            if 'accounts' in data:
                potential_lists.append(data['accounts'])
            if 'users' in data:
                potential_lists.append(data['users'])
            if 'data' in data and isinstance(data['data'], list):
                potential_lists.append(data['data'])
            
            for account_list in potential_lists:
                if isinstance(account_list, list):
                    for account in account_list[:max_accounts]:
                        if isinstance(account, dict):
                            username = account.get('username')
                            if username:
                                similar_users.append({
                                    'username': username,
                                    'found_from': f'similar_to_{seed_username}',
                                    'profile_url': f"https://instagram.com/{username}",
                                    'discovery_method': 'similar_accounts'
                                })
        
        elif isinstance(data, list):
            # Direct list format (most common for working responses)
            print(f"      ✅ Found {len(data)} similar accounts for @{seed_username}")
            for account in data[:max_accounts]:
                if isinstance(account, dict):
                    username = account.get('username')
                    if username:
                        similar_users.append({
                            'username': username,
                            'found_from': f'similar_to_{seed_username}',
                            'profile_url': f"https://instagram.com/{username}",
                            'discovery_method': 'similar_accounts'
                        })
        
        return similar_users
    
    def _extract_users_from_posts(self, data: Dict, source_name: str) -> List[Dict]:
        """Extract user data from hashtag posts structure"""
        
        page_users = {}
        posts_sources = []
        
        if 'posts' in data and isinstance(data['posts'], dict):
            posts_edges = data['posts'].get('edges', [])
            posts_sources.append(('posts', posts_edges))
            
        if 'top_posts' in data and isinstance(data['top_posts'], dict):
            top_posts_edges = data['top_posts'].get('edges', [])
            posts_sources.append(('top_posts', top_posts_edges))
        
        for source_type, edges in posts_sources:
            print(f"  📊 {source_name} - Processing {len(edges)} posts from {source_type}")
            
            for edge in edges:
                if not isinstance(edge, dict) or 'node' not in edge:
                    continue
                    
                node = edge['node']
                user_data = self._extract_user_from_post_node(node)
                
                if user_data and user_data.get('username'):
                    username = user_data['username']
                    if username not in page_users:
                        page_users[username] = user_data
        
        return list(page_users.values())
    
    def _extract_user_from_post_node(self, node: Dict) -> Optional[Dict]:
        """Extract user information from a post node"""
        
        user_id = None
        if 'owner' in node and isinstance(node['owner'], dict):
            user_id = node['owner'].get('id')
        
        username = None
        if 'accessibility_caption' in node:
            caption = node['accessibility_caption']
            username = self._extract_username_from_caption(caption)
        
        shortcode = node.get('shortcode', '')
        
        if username:
            return {
                'user_id': user_id,
                'username': username,
                'shortcode': shortcode,
                'post_url': f"https://instagram.com/p/{shortcode}" if shortcode else None,
                'profile_url': f"https://instagram.com/{username}",
                'found_from': 'hashtag_search',
                'discovery_method': 'hashtag_posts'
            }
        
        return None
    
    def _extract_username_from_caption(self, caption: str) -> Optional[str]:
        """Extract username from accessibility caption"""
        
        if not caption:
            return None
            
        patterns = [
            r'Photo shared by ([a-zA-Z0-9_.]+) on',
            r'Video shared by ([a-zA-Z0-9_.]+) on',
            r'Reel shared by ([a-zA-Z0-9_.]+) on',
            r'shared by ([a-zA-Z0-9_.]+) on',
            r'by (@?[a-zA-Z0-9_.]+)(?:\s|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, caption, re.IGNORECASE)
            if match:
                username = match.group(1).replace('@', '')
                if re.match(r'^[a-zA-Z0-9_.]+$', username) and len(username) <= 30:
                    return username
        
        return None
    
    def get_profile_details(self, username: str) -> Optional[Dict]:
        """Get detailed profile information including follower count - WORKING! ✅"""
        
        url = f"{self.base_url}/ig_get_fb_profile_hover.php?username_or_url={username}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'user_data' in data:
                    user_data = data['user_data']
                    
                    return {
                        'username': user_data.get('username', username),
                        'full_name': user_data.get('full_name', ''),
                        'followers': user_data.get('follower_count', 0),
                        'following': user_data.get('following_count', 0),
                        'posts': user_data.get('media_count', 0),
                        'verified': user_data.get('is_verified', False),
                        'private': user_data.get('is_private', False),
                        'profile_pic_url': user_data.get('profile_pic_url', ''),
                        'data_source': 'profile_api_success'
                    }
            
            return None
            
        except requests.exceptions.RequestException:
            return None
    
    def enrich_profiles_with_details(self, users: List[Dict], max_workers: int = 5) -> List[Dict]:
        """Fetch detailed profile information for each user"""
        
        print(f"\n🔍 Fetching detailed profile data for {len(users)} users...")
        print(f"📊 Using {max_workers} concurrent workers for faster processing")
        
        enriched_profiles = []
        
        def fetch_profile(user):
            username = user.get('username')
            if not username:
                return None
                
            profile_details = self.get_profile_details(username)
            
            if profile_details and profile_details.get('data_source') == 'profile_api_success':
                enriched_profile = {
                    **user,  # Original data (discovery method, post_url, etc.)
                    **profile_details,  # Detailed profile data
                }
                followers = profile_details.get('followers', 0)
                return enriched_profile
            else:
                return {
                    **user,
                    'full_name': '',
                    'followers': 0,
                    'following': 0,
                    'posts': 0,
                    'verified': False,
                    'private': False,
                    'data_source': 'basic_only'
                }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_user = {executor.submit(fetch_profile, user): user for user in users}
            
            for future in as_completed(future_to_user):
                result = future.result()
                if result:
                    enriched_profiles.append(result)
                    username = result.get('username', 'Unknown')
                    followers = result.get('followers', 0)
                    print(f"  ✅ @{username}: {self._format_number(followers)} followers")
        
        print(f"\n✅ Profile enrichment complete! {len(enriched_profiles)} profiles processed")
        return enriched_profiles
    
    def _format_number(self, num: int) -> str:
        """Format large numbers with K, M, B suffixes"""
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)
    
    def print_results(self, profiles: List[Dict], search_term: str, search_type: str):
        """Print formatted results with full profile data"""
        
        if not profiles:
            print(f"\n❌ No profiles found for {search_type}: {search_term}")
            return
        
        profiles_with_followers = [p for p in profiles if p.get('followers', 0) > 0]
        
        print(f"\n🎯 Found {len(profiles)} profiles for {search_type}: {search_term}")
        print(f"📊 {len(profiles_with_followers)} profiles have follower data")
        print("=" * 120)
        
        # Sort by follower count (descending)
        sorted_profiles = sorted(profiles, key=lambda x: x.get('followers', 0), reverse=True)
        
        for i, profile in enumerate(sorted_profiles, 1):
            verified_icon = " ✓" if profile.get('verified') else ""
            private_icon = " 🔒" if profile.get('private') else ""
            
            followers_formatted = self._format_number(profile.get('followers', 0))
            following_formatted = self._format_number(profile.get('following', 0))
            posts_formatted = self._format_number(profile.get('posts', 0))
            
            discovery_method = profile.get('discovery_method', 'unknown')
            discovery_icon = "🔍" if discovery_method == 'hashtag_posts' else "🎯" if discovery_method == 'similar_accounts' else "📱"
            
            print(f"\n{i:2d}. @{profile.get('username', 'Unknown')}{verified_icon}{private_icon} {discovery_icon}")
            
            if profile.get('full_name'):
                print(f"    Name: {profile['full_name']}")
            
            print(f"    👥 Followers: {followers_formatted}")
            print(f"    👣 Following: {following_formatted}")
            print(f"    📸 Posts: {posts_formatted}")
            print(f"    🔗 Profile: https://instagram.com/{profile.get('username', '')}")
            
            if profile.get('post_url'):
                print(f"    📱 Sample Post: {profile['post_url']}")
            
            # Show discovery method
            found_from = profile.get('found_from', 'unknown')
            if discovery_method == 'hashtag_posts':
                print(f"    🔍 Discovered: From hashtag posts")
            elif discovery_method == 'similar_accounts':
                print(f"    🎯 Discovered: Similar to {found_from.replace('similar_to_', '@')}")
    
    def save_to_json(self, profiles: List[Dict], search_term: str, search_type: str):
        """Save comprehensive results to JSON file"""
        
        timestamp = int(time.time())
        filename = f"instagram_ultimate_{search_type}_{search_term}_{timestamp}.json"
        
        profiles_with_followers = [p for p in profiles if p.get('followers', 0) > 0]
        hashtag_profiles = [p for p in profiles if p.get('discovery_method') == 'hashtag_posts']
        similar_profiles = [p for p in profiles if p.get('discovery_method') == 'similar_accounts']
        
        data = {
            'search_term': search_term,
            'search_type': search_type,
            'search_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_profiles': len(profiles),
            'profiles_with_follower_data': len(profiles_with_followers),
            'discovery_breakdown': {
                'hashtag_posts': len(hashtag_profiles),
                'similar_accounts': len(similar_profiles)
            },
            'api_endpoints_used': [
                '/search_hashtag.php (with pagination) ✅ WORKING',
                '/get_ig_similar_accounts.php ✅ WORKING',
                '/ig_get_fb_profile_hover.php ✅ WORKING'
            ],
            'features': [
                'hashtag_discovery', 'similar_accounts_discovery', 'pagination',
                'follower_counts', 'following_counts', 'verification_status',
                'privacy_indicators', 'profile_urls', 'sample_posts'
            ],
            'profiles': profiles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Ultimate results saved to {filename}")

def main():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        print("❌ Missing INSTAGRAM_API_KEY environment variable")
        sys.exit(1)
    
    # Get search term and method from command line
    if len(sys.argv) < 2:
        print("🚀 Instagram Ultimate Profile Scraper")
        print("💡 Usage:")
        print(f"   python3 {sys.argv[0]} hashtag <hashtag> [max_pages]")
        print(f"   python3 {sys.argv[0]} similar <username> [max_similar_per_seed]")
        print(f"   python3 {sys.argv[0]} combined <hashtag> [max_pages] [max_similar_per_seed]")
        print("\n📋 Examples:")
        print(f"   python3 {sys.argv[0]} hashtag luxury 3")
        print(f"   python3 {sys.argv[0]} similar insightsgta 10")
        print(f"   python3 {sys.argv[0]} combined luxury 2 5")
        return
    
    search_type = sys.argv[1].lower()
    
    if search_type not in ['hashtag', 'similar', 'combined']:
        print("❌ Invalid search type. Use: hashtag, similar, or combined")
        return
    
    search_term = sys.argv[2] if len(sys.argv) > 2 else "luxury"
    
    scraper = InstagramUltimateScraperr(API_KEY)
    all_profiles = []
    
    print("🚀 Instagram Ultimate Profile Scraper")
    print(f"🔑 Using RapidAPI Instagram Scraper Stable API")
    print(f"🎯 Search type: {search_type.upper()}")
    print(f"🔍 Search term: {search_term}")
    
    if search_type in ['hashtag', 'combined']:
        # Hashtag search
        max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        print(f"📄 Hashtag pages: {max_pages}")
        
        hashtag_profiles = scraper.search_hashtag_with_pagination(search_term, max_pages)
        all_profiles.extend(hashtag_profiles)
    
    if search_type in ['similar', 'combined']:
        # Similar accounts search
        if search_type == 'similar':
            # Use the provided username directly
            seed_usernames = [search_term]
            max_similar = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        else:
            # Use top profiles from hashtag search as seeds
            seed_usernames = [p['username'] for p in all_profiles[:5] if p.get('username')]
            max_similar = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        
        print(f"🎯 Similar accounts per seed: {max_similar}")
        
        if seed_usernames:
            similar_profiles = scraper.find_similar_accounts(seed_usernames, max_similar)
            all_profiles.extend(similar_profiles)
    
    if all_profiles:
        # Remove duplicates based on username
        unique_profiles = {}
        for profile in all_profiles:
            username = profile.get('username')
            if username and username not in unique_profiles:
                unique_profiles[username] = profile
        
        final_profiles = list(unique_profiles.values())
        
        # Enrich with detailed data
        enriched_profiles = scraper.enrich_profiles_with_details(final_profiles)
        
        if enriched_profiles:
            # Display results
            scraper.print_results(enriched_profiles, search_term, search_type)
            
            # Save to JSON
            scraper.save_to_json(enriched_profiles, search_term, search_type)
            
            print(f"\n✅ Ultimate search finished!")
            print(f"📊 Summary: {len(enriched_profiles)} unique profiles discovered")
            
            # Show discovery breakdown
            hashtag_count = len([p for p in enriched_profiles if p.get('discovery_method') == 'hashtag_posts'])
            similar_count = len([p for p in enriched_profiles if p.get('discovery_method') == 'similar_accounts'])
            
            if hashtag_count > 0:
                print(f"🔍 Hashtag discovery: {hashtag_count} profiles")
            if similar_count > 0:
                print(f"🎯 Similar accounts: {similar_count} profiles")
            
            # Show top profile
            if enriched_profiles:
                top_profile = enriched_profiles[0]
                followers = top_profile.get('followers', 0)
                print(f"👑 Top profile: @{top_profile.get('username')} with {scraper._format_number(followers)} followers")
        else:
            print(f"\n⚠️  Could not enrich profiles with detailed data")
    else:
        print(f"\n❌ No profiles found")

if __name__ == "__main__":
    main() 