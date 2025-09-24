#!/usr/bin/env python3
"""
Instagram Interactive Discovery System - USER CUSTOMIZABLE
🎯 Interactive: Choose hashtag, target profiles, and min followers
🔍 Smart filtering: BFS expansion through similar accounts
📊 Output: CSV file with your custom criteria
"""

import requests
import json
import sys
import time
import re
import csv
import argparse
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

class InteractiveInstagramDiscovery:
    def __init__(self, api_key: str, target_profiles: int = 500, min_followers: int = 50000):
        self.api_key = api_key
        self.base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
        }
        
        # User-customizable settings
        self.TARGET_PROFILES = target_profiles
        self.MIN_FOLLOWERS = min_followers
        
        # Discovery tracking
        self.discovered_usernames: Set[str] = set()
        self.high_follower_profiles: List[ProfileData] = []
        self.discovery_queue: Deque[Dict] = deque()
        self.total_api_calls = 0
        
        # Fixed configuration
        self.MAX_DISCOVERY_DEPTH = 5
        self.SIMILAR_ACCOUNTS_PER_USER = 30
        self.MAX_HASHTAG_PAGES = 3
        
    def discover_profiles(self, hashtag: str) -> List[ProfileData]:
        """
        Discover profiles based on user criteria
        """
        
        print(f"🚀 Starting Instagram Discovery")
        print(f"🎯 Target: {self.TARGET_PROFILES} profiles with {self.MIN_FOLLOWERS:,}+ followers")
        print(f"🔍 Starting hashtag: #{hashtag}")
        print(f"🧠 Strategy: Hashtag seeds → BFS similar accounts → Filter by followers")
        print("=" * 100)
        
        # Phase 1: Get seed accounts
        print(f"\n🌱 PHASE 1: Collecting Seed Accounts")
        seed_accounts = self._get_hashtag_seeds(hashtag)
        
        if not seed_accounts:
            print("❌ No seed accounts found! Trying alternate hashtags...")
            # Try related hashtags based on input
            alternate_hashtags = self._get_related_hashtags(hashtag)
            for alt_hashtag in alternate_hashtags:
                print(f"🔄 Trying #{alt_hashtag}...")
                seed_accounts = self._get_hashtag_seeds(alt_hashtag)
                if seed_accounts:
                    break
        
        if not seed_accounts:
            print("❌ Could not find any seed accounts! Try a different hashtag.")
            return []
        
        print(f"✅ Collected {len(seed_accounts)} seed accounts")
        
        # Phase 2: BFS expansion
        print(f"\n🔍 PHASE 2: BFS Expansion")
        self._smart_bfs_discovery(seed_accounts)
        
        # Phase 3: Results
        print(f"\n📊 PHASE 3: Results Summary")
        self._print_discovery_summary()
        
        return self.high_follower_profiles
    
    def _get_related_hashtags(self, hashtag: str) -> List[str]:
        """Get related hashtags as fallbacks"""
        
        hashtag_families = {
            'luxury': ['fashion', 'lifestyle', 'style', 'designer', 'premium'],
            'fashion': ['style', 'ootd', 'outfit', 'clothing', 'designer'],
            'business': ['entrepreneur', 'startup', 'marketing', 'success', 'money'],
            'gaming': ['gamer', 'esports', 'videogames', 'streaming', 'twitch'],
            'fitness': ['gym', 'workout', 'health', 'bodybuilding', 'crossfit'],
            'travel': ['vacation', 'adventure', 'explore', 'wanderlust', 'trip'],
            'food': ['foodie', 'cooking', 'recipe', 'restaurant', 'chef'],
            'tech': ['technology', 'coding', 'programming', 'startup', 'innovation']
        }
        
        # Find related hashtags
        for key, related in hashtag_families.items():
            if key in hashtag.lower():
                return related
        
        # Default fallbacks
        return ['lifestyle', 'style', 'business', 'entrepreneur', 'success']
    
    def _get_hashtag_seeds(self, hashtag: str) -> List[str]:
        """Get seed usernames from hashtag"""
        
        seed_usernames = []
        
        for page in range(1, self.MAX_HASHTAG_PAGES + 1):
            print(f"  📄 Page {page}")
            
            page_usernames = self._search_hashtag_page(hashtag)
            seed_usernames.extend(page_usernames)
            
            print(f"    Found {len(page_usernames)} usernames")
            
            if len(seed_usernames) >= 50:
                break
                
            time.sleep(1)
        
        # Remove duplicates
        unique_seeds = list(set(seed_usernames))
        return unique_seeds[:100]  # Limit to 100 seeds
    
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
        """Extract usernames from hashtag posts via caption parsing"""
        
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
                    
                    # Extract from accessibility caption
                    if 'accessibility_caption' in node:
                        caption = node['accessibility_caption']
                        username = self._extract_username_from_caption(caption)
                        if username:
                            usernames.append(username)
        
        return list(set(usernames))
    
    def _extract_username_from_caption(self, caption: str) -> Optional[str]:
        """Extract username from accessibility caption"""
        
        if not caption:
            return None
            
        patterns = [
            # Current format
            r'Photo by ([a-zA-Z0-9_.]+) on',
            r'Video by ([a-zA-Z0-9_.]+) on',
            r'Reel by ([a-zA-Z0-9_.]+) on',
            
            # Backup patterns
            r'Photo shared by ([a-zA-Z0-9_.]+) on',
            r'Video shared by ([a-zA-Z0-9_.]+) on',
            r'Reel shared by ([a-zA-Z0-9_.]+) on',
            r'shared by ([a-zA-Z0-9_.]+) on',
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
        
        if not re.match(r'^[a-zA-Z0-9_.]+$', username):
            return False
        
        if len(username) > 30 or len(username) < 1:
            return False
        
        # Avoid false positives
        common_words = {'instagram', 'photo', 'video', 'image', 'picture', 'post', 'story'}
        if username.lower() in common_words:
            return False
        
        return True
    
    def _smart_bfs_discovery(self, seed_usernames: List[str]):
        """Smart BFS discovery through similar accounts"""
        
        # Initialize queue
        for username in seed_usernames:
            if username not in self.discovered_usernames:
                self.discovery_queue.append({
                    'username': username,
                    'depth': 0,
                    'parent': 'hashtag_seed',
                    'priority': 0
                })
                self.discovered_usernames.add(username)
        
        processed_count = 0
        progress_interval = max(1, self.TARGET_PROFILES // 20)  # Show progress every 5%
        
        print(f"  🚀 Starting BFS with {len(self.discovery_queue)} seed accounts")
        
        while self.discovery_queue and len(self.high_follower_profiles) < self.TARGET_PROFILES:
            current = self.discovery_queue.popleft()
            processed_count += 1
            
            username = current['username']
            depth = current['depth']
            parent = current['parent']
            
            print(f"\n  🔍 [{processed_count}] @{username} (depth {depth})")
            print(f"      📊 Queue: {len(self.discovery_queue)}, Found {self.MIN_FOLLOWERS//1000}k+: {len(self.high_follower_profiles)}")
            
            # Get profile details
            profile_data = self._get_profile_details(username)
            
            if profile_data:
                followers = profile_data.followers
                print(f"      👥 {self._format_number(followers)} followers", end="")
                
                # Check if qualifies
                if followers >= self.MIN_FOLLOWERS:
                    profile_data.discovery_path = f"depth_{depth}_from_{parent}"
                    profile_data.discovery_depth = depth
                    self.high_follower_profiles.append(profile_data)
                    
                    print(f" ✅ QUALIFIED! ({len(self.high_follower_profiles)}/{self.TARGET_PROFILES})")
                    
                    if len(self.high_follower_profiles) >= self.TARGET_PROFILES:
                        print(f"      🎯 TARGET REACHED!")
                        break
                else:
                    print("")
                
                # Expand through similar accounts
                if depth < self.MAX_DISCOVERY_DEPTH:
                    similar_count = self.SIMILAR_ACCOUNTS_PER_USER
                    if followers >= self.MIN_FOLLOWERS // 5:  # Get more similar for promising accounts
                        similar_count = min(50, self.SIMILAR_ACCOUNTS_PER_USER * 2)
                    
                    similar_accounts = self._get_similar_accounts(username, similar_count)
                    
                    added_count = 0
                    for similar in similar_accounts:
                        similar_username = similar.get('username')
                        if similar_username and similar_username not in self.discovered_usernames:
                            # Priority based on followers
                            priority = 1 if followers >= self.MIN_FOLLOWERS // 5 else 2 if followers >= 1000 else 3
                            
                            self.discovery_queue.append({
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
            
            # Progress update
            if processed_count % progress_interval == 0:
                progress = (len(self.high_follower_profiles) / self.TARGET_PROFILES) * 100
                print(f"\n  📊 PROGRESS: {progress:.1f}% complete ({len(self.high_follower_profiles)}/{self.TARGET_PROFILES})")
            
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
        print(f"🎯 DISCOVERY COMPLETE!")
        print(f"="*100)
        print(f"📊 Profiles found: {len(self.high_follower_profiles)}")
        print(f"🎯 Target: {self.TARGET_PROFILES} profiles with {self.MIN_FOLLOWERS:,}+ followers")
        print(f"📞 Total API calls: {self.total_api_calls}")
        print(f"🔍 Accounts discovered: {len(self.discovered_usernames)}")
        
        if self.high_follower_profiles:
            sorted_profiles = sorted(self.high_follower_profiles, key=lambda x: x.followers, reverse=True)
            
            print(f"\n🏆 TOP 10 DISCOVERIES:")
            for i, profile in enumerate(sorted_profiles[:10], 1):
                verified_icon = " ✓" if profile.verified else ""
                private_icon = " 🔒" if profile.private else ""
                print(f"  {i:2d}. @{profile.username}{verified_icon}{private_icon}")
                print(f"      👥 {self._format_number(profile.followers)} followers")
    
    def export_to_csv(self, filename: str = None):
        """Export to CSV"""
        
        if not filename:
            timestamp = int(time.time())
            min_followers_k = self.MIN_FOLLOWERS // 1000
            filename = f"instagram_{len(self.high_follower_profiles)}_profiles_{min_followers_k}k+_{timestamp}.csv"
        
        if not self.high_follower_profiles:
            print("❌ No profiles to export")
            return
        
        sorted_profiles = sorted(self.high_follower_profiles, key=lambda x: x.followers, reverse=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'rank', 'username', 'full_name', 'followers', 'following', 'posts',
                'verified', 'private', 'profile_url', 'discovery_path', 'discovery_depth'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, profile in enumerate(sorted_profiles, 1):
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
        print(f"📁 File: {filename}")
        print(f"📊 Exported: {len(sorted_profiles)} profiles")
        if sorted_profiles:
            print(f"👥 Follower range: {self._format_number(sorted_profiles[-1].followers)} - {self._format_number(sorted_profiles[0].followers)}")

def get_user_input():
    """Get user input interactively"""
    
    print("🎯 Instagram Profile Discovery - Interactive Setup")
    print("=" * 60)
    
    # Get hashtag
    hashtag = input("📝 Enter hashtag to search (without #): ").strip()
    if not hashtag:
        hashtag = "luxury"
        print(f"   Using default: {hashtag}")
    
    # Get target number of profiles
    while True:
        try:
            target_input = input("🎯 How many profiles do you want to find? (default: 100): ").strip()
            if not target_input:
                target_profiles = 100
            else:
                target_profiles = int(target_input)
            
            if target_profiles > 0:
                break
            else:
                print("   Please enter a positive number")
        except ValueError:
            print("   Please enter a valid number")
    
    # Get minimum followers
    while True:
        try:
            min_followers_input = input("👥 Minimum followers required (e.g., 50000, 10000): ").strip()
            if not min_followers_input:
                min_followers = 50000
            else:
                min_followers = int(min_followers_input)
            
            if min_followers > 0:
                break
            else:
                print("   Please enter a positive number")
        except ValueError:
            print("   Please enter a valid number")
    
    return hashtag, target_profiles, min_followers

def main():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        print("❌ Missing INSTAGRAM_API_KEY environment variable")
        sys.exit(1)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Instagram Profile Discovery')
    parser.add_argument('hashtag', nargs='?', help='Hashtag to search (without #)')
    parser.add_argument('-n', '--number', type=int, help='Number of profiles to find')
    parser.add_argument('-f', '--followers', type=int, help='Minimum followers required')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    # Determine input method
    if args.interactive or (not args.hashtag and len(sys.argv) == 1):
        hashtag, target_profiles, min_followers = get_user_input()
    else:
        hashtag = args.hashtag or "luxury"
        target_profiles = args.number or 100
        min_followers = args.followers or 50000
    
    print(f"\n🚀 Starting Discovery:")
    print(f"   📝 Hashtag: #{hashtag}")
    print(f"   🎯 Target: {target_profiles} profiles")
    print(f"   👥 Min followers: {min_followers:,}")
    print(f"   ⏱️  Estimated time: {target_profiles // 10}-{target_profiles // 5} minutes")
    
    # Confirm before starting
    confirm = input(f"\n▶️  Start discovery? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '']:
        print("❌ Discovery cancelled")
        return
    
    # Start discovery
    discovery = InteractiveInstagramDiscovery(API_KEY, target_profiles, min_followers)
    profiles = discovery.discover_profiles(hashtag)
    discovery.export_to_csv()
    
    print(f"\n✅ Discovery complete! Found {len(profiles)} profiles")

if __name__ == "__main__":
    main() 