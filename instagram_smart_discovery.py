#!/usr/bin/env python3
"""
Instagram Smart Discovery System - FIND 500 PROFILES WITH 50K+ FOLLOWERS
🎯 Strategy: Start with ANY hashtag accounts → Expand through similar accounts → Filter for 50k+
🧠 Smart approach: Cast wide net first, then filter for high followers in similar accounts
📊 Output: CSV file with 500 high-follower profiles
"""

import requests
import json
import sys
import time
import re
import csv
from typing import List, Dict, Optional, Set, Deque
from collections import deque
from dataclasses import dataclass

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
    discovery_path: str
    discovery_depth: int

class SmartInstagramDiscovery:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
        }
        
        # Discovery tracking
        self.discovered_usernames: Set[str] = set()
        self.high_follower_profiles: List[ProfileData] = []
        self.discovery_queue: Deque[Dict] = deque()
        self.total_api_calls = 0
        
        # Configuration
        self.TARGET_PROFILES = 500
        self.MIN_FOLLOWERS = 50000
        self.MAX_DISCOVERY_DEPTH = 5
        self.SIMILAR_ACCOUNTS_PER_USER = 30
        self.MAX_HASHTAG_PAGES = 3
        
    def discover_500_profiles(self, hashtag: str) -> List[ProfileData]:
        """
        Smart discovery method: Start with any hashtag accounts, expand to find 50k+ followers
        Strategy: Hashtag ANY accounts → Similar accounts → Filter for 50k+ → Expand further
        """
        
        print(f"🚀 Starting Smart Instagram Discovery")
        print(f"🎯 Target: {self.TARGET_PROFILES} profiles with {self.MIN_FOLLOWERS:,}+ followers")
        print(f"🔍 Starting hashtag: #{hashtag}")
        print(f"🧠 Strategy: Cast wide net → Expand through similar accounts → Filter for high followers")
        print("=" * 100)
        
        # Phase 1: Get ANY accounts from hashtag (seeds)
        print(f"\n🌱 PHASE 1: Collecting Seed Accounts (ANY follower count)")
        seed_accounts = self._get_hashtag_seeds(hashtag)
        
        if not seed_accounts:
            print("❌ No seed accounts found! Trying alternate hashtags...")
            # Try related hashtags
            alternate_hashtags = ["fashion", "lifestyle", "style", "business", "entrepreneur"]
            for alt_hashtag in alternate_hashtags:
                print(f"🔄 Trying #{alt_hashtag}...")
                seed_accounts = self._get_hashtag_seeds(alt_hashtag)
                if seed_accounts:
                    break
        
        print(f"✅ Collected {len(seed_accounts)} seed accounts")
        
        # Phase 2: BFS Expansion with Smart Filtering
        print(f"\n🔍 PHASE 2: BFS Expansion to Find High-Follower Profiles")
        self._smart_bfs_discovery(seed_accounts)
        
        # Phase 3: Results
        print(f"\n📊 PHASE 3: Results Summary")
        self._print_discovery_summary()
        
        return self.high_follower_profiles
    
    def _get_hashtag_seeds(self, hashtag: str) -> List[str]:
        """Get seed usernames from hashtag (accept ANY follower count)"""
        
        seed_usernames = []
        
        for page in range(1, self.MAX_HASHTAG_PAGES + 1):
            print(f"  📄 Hashtag page {page}")
            
            page_usernames = self._search_hashtag_page(hashtag)
            seed_usernames.extend(page_usernames)
            
            print(f"    Found {len(page_usernames)} usernames")
            
            if len(seed_usernames) >= 50:  # Get at least 50 seeds
                break
                
            time.sleep(1)
        
        # Remove duplicates
        unique_seeds = list(set(seed_usernames))
        return unique_seeds[:100]  # Limit to 100 seeds for efficiency
    
    def _search_hashtag_page(self, hashtag: str) -> List[str]:
        """Get usernames from hashtag page"""
        
        clean_hashtag = hashtag.replace('#', '')
        url = f"{self.base_url}/search_hashtag.php?hashtag={clean_hashtag}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            self.total_api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                return self._extract_usernames_from_posts(data)
            else:
                print(f"      ❌ Failed: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"      ❌ Error: {e}")
            return []
    
    def _extract_usernames_from_posts(self, data: Dict) -> List[str]:
        """Extract usernames from hashtag posts via caption parsing (only working method)"""
        
        usernames = []
        
        # Get posts from both regular and top posts
        posts_sources = []
        if 'posts' in data and isinstance(data['posts'], dict):
            posts_edges = data['posts'].get('edges', [])
            posts_sources.append(('posts', posts_edges))
            
        if 'top_posts' in data and isinstance(data['top_posts'], dict):
            top_posts_edges = data['top_posts'].get('edges', [])
            posts_sources.append(('top_posts', top_posts_edges))
        
        for source_type, edges in posts_sources:
            for edge in edges:
                if isinstance(edge, dict) and 'node' in edge:
                    node = edge['node']
                    
                    # Extract from accessibility caption (only working method for this API)
                    if 'accessibility_caption' in node:
                        caption = node['accessibility_caption']
                        username = self._extract_username_from_caption(caption)
                        if username:
                            usernames.append(username)
        
        # Remove duplicates and return
        return list(set(usernames))
    
    def _extract_username_from_caption(self, caption: str) -> Optional[str]:
        """Extract username from accessibility caption with FIXED patterns"""
        
        if not caption:
            return None
            
        # ✅ FIXED: Updated patterns for current Instagram format
        patterns = [
            # New format: "Photo by username on"
            r'Photo by ([a-zA-Z0-9_.]+) on',
            r'Video by ([a-zA-Z0-9_.]+) on',
            r'Reel by ([a-zA-Z0-9_.]+) on',
            
            # Old format (backup)
            r'Photo shared by ([a-zA-Z0-9_.]+) on',
            r'Video shared by ([a-zA-Z0-9_.]+) on',
            r'Reel shared by ([a-zA-Z0-9_.]+) on',
            r'shared by ([a-zA-Z0-9_.]+) on',
            
            # Additional patterns
            r'Photo shared by ([a-zA-Z0-9_.]+) tagging',
            r'by ([a-zA-Z0-9_.]+) in [A-Za-z]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, caption, re.IGNORECASE)
            if match:
                username = match.group(1)
                if self._is_valid_username(username):
                    return username
        
        return None
    
    def _is_valid_username(self, username: str) -> bool:
        """Check if username is valid Instagram format"""
        if not username:
            return False
        
        # Instagram username rules: 1-30 chars, alphanumeric + dots + underscores
        if not re.match(r'^[a-zA-Z0-9_.]+$', username):
            return False
        
        if len(username) > 30 or len(username) < 1:
            return False
        
        # Avoid common false positives
        common_words = {'instagram', 'photo', 'video', 'image', 'picture', 'post', 'story'}
        if username.lower() in common_words:
            return False
        
        return True
    
    def _smart_bfs_discovery(self, seed_usernames: List[str]):
        """Smart BFS: Expand through similar accounts, prioritize high-follower profiles"""
        
        # Initialize queue with seeds
        for username in seed_usernames:
            if username not in self.discovered_usernames:
                self.discovery_queue.append({
                    'username': username,
                    'depth': 0,
                    'parent': 'hashtag_seed',
                    'priority': 0  # Seeds have lowest priority
                })
                self.discovered_usernames.add(username)
        
        processed_count = 0
        high_follower_found_this_round = 0
        
        print(f"  🚀 Starting BFS with {len(self.discovery_queue)} seed accounts")
        
        while self.discovery_queue and len(self.high_follower_profiles) < self.TARGET_PROFILES:
            current = self.discovery_queue.popleft()
            processed_count += 1
            
            username = current['username']
            depth = current['depth']
            parent = current['parent']
            
            print(f"\n  🔍 [{processed_count}] @{username} (depth {depth})")
            print(f"      📊 Queue: {len(self.discovery_queue)}, Found 50k+: {len(self.high_follower_profiles)}")
            
            # Get profile details
            profile_data = self._get_profile_details(username)
            
            if profile_data:
                followers = profile_data.followers
                print(f"      👥 {self._format_number(followers)} followers", end="")
                
                # Check if qualifies for our target
                if followers >= self.MIN_FOLLOWERS:
                    profile_data.discovery_path = f"depth_{depth}_from_{parent}"
                    profile_data.discovery_depth = depth
                    self.high_follower_profiles.append(profile_data)
                    high_follower_found_this_round += 1
                    
                    print(f" ✅ QUALIFIED! ({len(self.high_follower_profiles)}/{self.TARGET_PROFILES})")
                    
                    if len(self.high_follower_profiles) >= self.TARGET_PROFILES:
                        print(f"      🎯 TARGET REACHED!")
                        break
                else:
                    print("")
                
                # Expand through similar accounts (prioritize accounts with more followers)
                if depth < self.MAX_DISCOVERY_DEPTH:
                    # Get more similar accounts for higher-follower users
                    similar_count = self.SIMILAR_ACCOUNTS_PER_USER
                    if followers >= 10000:  # If 10k+ followers, get more similar accounts
                        similar_count = min(50, self.SIMILAR_ACCOUNTS_PER_USER * 2)
                    
                    similar_accounts = self._get_similar_accounts(username, similar_count)
                    
                    added_count = 0
                    for similar in similar_accounts:
                        similar_username = similar.get('username')
                        if similar_username and similar_username not in self.discovered_usernames:
                            # Priority: higher follower accounts get processed first
                            priority = 1 if followers >= 10000 else 2 if followers >= 1000 else 3
                            
                            # Insert with priority (lower numbers processed first)
                            insert_pos = 0
                            for i, queued_item in enumerate(self.discovery_queue):
                                if queued_item.get('priority', 3) > priority:
                                    insert_pos = i
                                    break
                                insert_pos = i + 1
                            
                            self.discovery_queue.insert(insert_pos, {
                                'username': similar_username,
                                'depth': depth + 1,
                                'parent': username,
                                'priority': priority
                            })
                            
                            self.discovered_usernames.add(similar_username)
                            added_count += 1
                    
                    print(f"      🎯 Added {added_count} similar accounts to queue")
                
            else:
                print(f"      ❌ Could not get profile data")
            
            # Progress update every 25 accounts
            if processed_count % 25 == 0:
                print(f"\n  📊 PROGRESS UPDATE:")
                print(f"      Processed: {processed_count} accounts")
                print(f"      Found 50k+: {len(self.high_follower_profiles)}")
                print(f"      Queue remaining: {len(self.discovery_queue)}")
                print(f"      Recent discoveries: {high_follower_found_this_round} in last round")
                high_follower_found_this_round = 0
            
            # Rate limiting
            time.sleep(0.5)
    
    def _get_profile_details(self, username: str) -> Optional[ProfileData]:
        """Get profile details"""
        
        url = f"{self.base_url}/ig_get_fb_profile_hover.php?username_or_url={username}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            self.total_api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'user_data' in data:
                    user_data = data['user_data']
                    
                    return ProfileData(
                        username=user_data.get('username', username),
                        full_name=user_data.get('full_name', ''),
                        followers=user_data.get('follower_count', 0),
                        following=user_data.get('following_count', 0),
                        posts=user_data.get('media_count', 0),
                        verified=user_data.get('is_verified', False),
                        private=user_data.get('is_private', False),
                        profile_url=f"https://instagram.com/{username}",
                        discovery_path="",
                        discovery_depth=0
                    )
            
            return None
            
        except requests.exceptions.RequestException:
            return None
    
    def _get_similar_accounts(self, username: str, max_accounts: int = 30) -> List[Dict]:
        """Get similar accounts"""
        
        url = f"{self.base_url}/get_ig_similar_accounts.php?username_or_url={username}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            self.total_api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    return [{'username': acc['username']} for acc in data[:max_accounts] 
                           if isinstance(acc, dict) and acc.get('username')]
                elif isinstance(data, dict) and 'error' not in data:
                    return []
            
            return []
            
        except requests.exceptions.RequestException:
            return []
    
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
    
    def _print_discovery_summary(self):
        """Print discovery summary"""
        
        print(f"\n" + "="*100)
        print(f"🎯 SMART DISCOVERY COMPLETE!")
        print(f"="*100)
        print(f"📊 Total qualified profiles: {len(self.high_follower_profiles)}")
        print(f"🎯 Target: {self.TARGET_PROFILES} profiles with {self.MIN_FOLLOWERS:,}+ followers")
        print(f"📞 Total API calls: {self.total_api_calls}")
        print(f"🔍 Unique accounts discovered: {len(self.discovered_usernames)}")
        
        if self.high_follower_profiles:
            sorted_profiles = sorted(self.high_follower_profiles, key=lambda x: x.followers, reverse=True)
            
            print(f"\n🏆 TOP 10 DISCOVERIES:")
            for i, profile in enumerate(sorted_profiles[:10], 1):
                verified_icon = " ✓" if profile.verified else ""
                private_icon = " 🔒" if profile.private else ""
                print(f"  {i:2d}. @{profile.username}{verified_icon}{private_icon}")
                print(f"      👥 {self._format_number(profile.followers)} followers")
                print(f"      📍 Discovery: {profile.discovery_path}")
            
            # Discovery depth analysis
            depth_counts = {}
            for profile in self.high_follower_profiles:
                depth = profile.discovery_depth
                depth_counts[depth] = depth_counts.get(depth, 0) + 1
            
            print(f"\n📊 DISCOVERY DEPTH BREAKDOWN:")
            for depth in sorted(depth_counts.keys()):
                print(f"  Depth {depth}: {depth_counts[depth]} profiles")
    
    def export_to_csv(self, filename: str = None):
        """Export to CSV"""
        
        if not filename:
            timestamp = int(time.time())
            filename = f"instagram_500_influencers_{timestamp}.csv"
        
        if not self.high_follower_profiles:
            print("❌ No profiles to export")
            return
        
        sorted_profiles = sorted(self.high_follower_profiles, key=lambda x: x.followers, reverse=True)
        profiles_to_export = sorted_profiles[:self.TARGET_PROFILES]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'rank', 'username', 'full_name', 'followers', 'following', 'posts',
                'verified', 'private', 'profile_url', 'discovery_path', 'discovery_depth'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, profile in enumerate(profiles_to_export, 1):
                writer.writerow({
                    'rank': i,
                    'username': profile.username,
                    'full_name': profile.full_name,
                    'followers': profile.followers,
                    'following': profile.following,
                    'posts': profile.posts,
                    'verified': profile.verified,
                    'private': profile.private,
                    'profile_url': profile.profile_url,
                    'discovery_path': profile.discovery_path,
                    'discovery_depth': profile.discovery_depth
                })
        
        print(f"\n💾 CSV EXPORT COMPLETE!")
        print(f"📁 Filename: {filename}")
        print(f"📊 Exported: {len(profiles_to_export)} profiles")
        if profiles_to_export:
            print(f"👥 Follower range: {self._format_number(profiles_to_export[-1].followers)} - {self._format_number(profiles_to_export[0].followers)}")

def main():
    import os, sys
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        print("❌ Missing INSTAGRAM_API_KEY environment variable")
        sys.exit(1)
    
    hashtag = sys.argv[1] if len(sys.argv) > 1 else "luxury"
    
    print("🚀 Instagram Smart Discovery System")
    print("🎯 Mission: Find 500 profiles with 50,000+ followers")
    print("🧠 Smart Strategy: Wide net → Similar accounts → High-follower filtering")
    print(f"📝 Starting hashtag: #{hashtag}")
    
    discovery = SmartInstagramDiscovery(API_KEY)
    profiles = discovery.discover_500_profiles(hashtag)
    discovery.export_to_csv()
    
    print(f"\n✅ Smart discovery mission complete!")

if __name__ == "__main__":
    main() 