#!/usr/bin/env python3
"""
Instagram Iterative Discovery System - FIND 500 PROFILES WITH 50K+ FOLLOWERS
🎯 Strategy: BFS discovery through hashtags → similar accounts → similar accounts (recursive)
🔍 Smart filtering: Only collect profiles with 50k+ followers
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
from concurrent.futures import ThreadPoolExecutor, as_completed
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

class IterativeInstagramDiscovery:
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
        self.MAX_DISCOVERY_DEPTH = 4
        self.SIMILAR_ACCOUNTS_PER_USER = 20
        self.MAX_HASHTAG_PAGES = 5
        
    def discover_500_profiles(self, hashtag: str) -> List[ProfileData]:
        """
        Main discovery method: Find 500 profiles with 50k+ followers
        Strategy: Hashtag search → Similar accounts → Similar of similar (BFS)
        """
        
        print(f"🚀 Starting Iterative Instagram Discovery")
        print(f"🎯 Target: {self.TARGET_PROFILES} profiles with {self.MIN_FOLLOWERS:,}+ followers")
        print(f"🔍 Starting hashtag: #{hashtag}")
        print(f"📊 Max depth: {self.MAX_DISCOVERY_DEPTH}, Similar per user: {self.SIMILAR_ACCOUNTS_PER_USER}")
        print("=" * 100)
        
        # Phase 1: Hashtag Discovery (Seed Collection)
        print(f"\n🌱 PHASE 1: Hashtag Seed Discovery")
        hashtag_seeds = self._discover_hashtag_seeds(hashtag)
        
        # Add seeds to discovery queue
        for seed in hashtag_seeds:
            if seed['username'] not in self.discovered_usernames:
                self.discovery_queue.append({
                    'username': seed['username'],
                    'depth': 0,
                    'parent': f"hashtag_#{hashtag}",
                    'discovery_path': f"#{hashtag}"
                })
                self.discovered_usernames.add(seed['username'])
        
        print(f"✅ Added {len(hashtag_seeds)} seed accounts to discovery queue")
        
        # Phase 2: BFS Similar Account Discovery
        print(f"\n🔍 PHASE 2: BFS Similar Account Discovery")
        self._bfs_similar_discovery()
        
        # Phase 3: Results and Export
        print(f"\n📊 PHASE 3: Results Collection")
        self._print_discovery_summary()
        
        return self.high_follower_profiles
    
    def _discover_hashtag_seeds(self, hashtag: str) -> List[Dict]:
        """Discover initial seed accounts from hashtag search with pagination"""
        
        all_seeds = []
        
        for page in range(1, self.MAX_HASHTAG_PAGES + 1):
            print(f"\n📄 Hashtag page {page}/{self.MAX_HASHTAG_PAGES}")
            
            # Get profiles from this hashtag page
            page_profiles = self._search_hashtag_page(hashtag, page)
            
            # Get profile details for high-potential accounts
            enriched_profiles = self._enrich_and_filter_profiles(page_profiles, f"hashtag_#{hashtag}_p{page}")
            
            all_seeds.extend(enriched_profiles)
            
            print(f"  ✅ Page {page}: Found {len(enriched_profiles)} qualifying profiles")
            print(f"  📊 Total high-follower profiles so far: {len(self.high_follower_profiles)}")
            
            if len(self.high_follower_profiles) >= self.TARGET_PROFILES:
                print(f"  🎯 Target reached! Stopping hashtag discovery.")
                break
                
            time.sleep(2)  # Rate limiting
        
        return all_seeds
    
    def _search_hashtag_page(self, hashtag: str, page_num: int) -> List[Dict]:
        """Search a specific hashtag page with pagination"""
        
        clean_hashtag = hashtag.replace('#', '')
        pagination_token = None
        
        # For page > 1, we need to build up pagination tokens
        # This is simplified - in practice you'd cache tokens
        url = f"{self.base_url}/search_hashtag.php?hashtag={clean_hashtag}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            self.total_api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                return self._extract_users_from_posts(data, f"hashtag_page_{page_num}")
            else:
                print(f"    ❌ Hashtag page {page_num} failed: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Network error on page {page_num}: {e}")
            return []
    
    def _extract_users_from_posts(self, data: Dict, source: str) -> List[Dict]:
        """Extract user data from hashtag posts"""
        
        users = []
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
                    user_data = self._extract_user_from_post_node(node, source)
                    if user_data:
                        users.append(user_data)
        
        # Remove duplicates
        unique_users = {}
        for user in users:
            username = user.get('username')
            if username and username not in unique_users:
                unique_users[username] = user
        
        return list(unique_users.values())
    
    def _extract_user_from_post_node(self, node: Dict, source: str) -> Optional[Dict]:
        """Extract user from post node"""
        
        username = None
        if 'accessibility_caption' in node:
            caption = node['accessibility_caption']
            username = self._extract_username_from_caption(caption)
        
        if username:
            return {
                'username': username,
                'source': source,
                'post_url': f"https://instagram.com/p/{node.get('shortcode', '')}"
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
        ]
        
        for pattern in patterns:
            match = re.search(pattern, caption, re.IGNORECASE)
            if match:
                username = match.group(1)
                if re.match(r'^[a-zA-Z0-9_.]+$', username) and len(username) <= 30:
                    return username
        
        return None
    
    def _bfs_similar_discovery(self):
        """BFS discovery through similar accounts"""
        
        processed_count = 0
        
        while self.discovery_queue and len(self.high_follower_profiles) < self.TARGET_PROFILES:
            current = self.discovery_queue.popleft()
            processed_count += 1
            
            username = current['username']
            depth = current['depth']
            parent = current['parent']
            discovery_path = current['discovery_path']
            
            print(f"\n🔍 Processing {processed_count}: @{username} (depth {depth})")
            print(f"    📍 Path: {discovery_path}")
            print(f"    📊 Queue size: {len(self.discovery_queue)}, High-follower found: {len(self.high_follower_profiles)}")
            
            # Get profile details for current user
            profile_data = self._get_profile_details(username)
            
            if profile_data:
                # Check if this profile qualifies (50k+ followers)
                if profile_data.followers >= self.MIN_FOLLOWERS:
                    profile_data.discovery_path = discovery_path
                    profile_data.discovery_depth = depth
                    self.high_follower_profiles.append(profile_data)
                    
                    print(f"    ✅ QUALIFIED: @{username} - {self._format_number(profile_data.followers)} followers")
                    
                    if len(self.high_follower_profiles) >= self.TARGET_PROFILES:
                        print(f"    🎯 TARGET REACHED! Found {self.TARGET_PROFILES} profiles")
                        break
                
                # If not at max depth, find similar accounts
                if depth < self.MAX_DISCOVERY_DEPTH:
                    similar_accounts = self._get_similar_accounts(username, max_accounts=self.SIMILAR_ACCOUNTS_PER_USER)
                    
                    added_to_queue = 0
                    for similar in similar_accounts:
                        similar_username = similar.get('username')
                        if similar_username and similar_username not in self.discovered_usernames:
                            self.discovery_queue.append({
                                'username': similar_username,
                                'depth': depth + 1,
                                'parent': username,
                                'discovery_path': f"{discovery_path} → @{username} → @{similar_username}"
                            })
                            self.discovered_usernames.add(similar_username)
                            added_to_queue += 1
                    
                    print(f"    🎯 Added {added_to_queue} similar accounts to queue")
                
            else:
                print(f"    ⚠️  Could not get profile details for @{username}")
            
            # Rate limiting
            time.sleep(1)
    
    def _enrich_and_filter_profiles(self, users: List[Dict], source: str) -> List[Dict]:
        """Get profile details and filter for high-follower accounts"""
        
        qualified_profiles = []
        
        for user in users:
            username = user.get('username')
            if not username:
                continue
                
            profile_data = self._get_profile_details(username)
            
            if profile_data and profile_data.followers >= self.MIN_FOLLOWERS:
                profile_data.discovery_path = source
                profile_data.discovery_depth = 0
                self.high_follower_profiles.append(profile_data)
                qualified_profiles.append(user)
                
                print(f"    ✅ @{username}: {self._format_number(profile_data.followers)} followers")
        
        return qualified_profiles
    
    def _get_profile_details(self, username: str) -> Optional[ProfileData]:
        """Get detailed profile information"""
        
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
    
    def _get_similar_accounts(self, username: str, max_accounts: int = 20) -> List[Dict]:
        """Get similar accounts for a username"""
        
        url = f"{self.base_url}/get_ig_similar_accounts.php?username_or_url={username}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            self.total_api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    similar_accounts = []
                    for account in data[:max_accounts]:
                        if isinstance(account, dict) and account.get('username'):
                            similar_accounts.append({
                                'username': account['username']
                            })
                    return similar_accounts
                elif isinstance(data, dict) and 'error' not in data:
                    # Handle nested structure if needed
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
        """Print discovery summary statistics"""
        
        print(f"\n" + "="*100)
        print(f"🎯 DISCOVERY COMPLETE!")
        print(f"="*100)
        print(f"📊 Total profiles found: {len(self.high_follower_profiles)}")
        print(f"🎯 Target: {self.TARGET_PROFILES} profiles with {self.MIN_FOLLOWERS:,}+ followers")
        print(f"📞 Total API calls made: {self.total_api_calls}")
        print(f"🔍 Unique usernames discovered: {len(self.discovered_usernames)}")
        
        if self.high_follower_profiles:
            # Sort by followers descending
            sorted_profiles = sorted(self.high_follower_profiles, key=lambda x: x.followers, reverse=True)
            
            print(f"\n🏆 TOP 10 PROFILES:")
            for i, profile in enumerate(sorted_profiles[:10], 1):
                verified_icon = " ✓" if profile.verified else ""
                private_icon = " 🔒" if profile.private else ""
                print(f"  {i:2d}. @{profile.username}{verified_icon}{private_icon} - {self._format_number(profile.followers)} followers")
            
            # Discovery depth analysis
            depth_counts = {}
            for profile in self.high_follower_profiles:
                depth = profile.discovery_depth
                depth_counts[depth] = depth_counts.get(depth, 0) + 1
            
            print(f"\n📊 DISCOVERY DEPTH BREAKDOWN:")
            for depth in sorted(depth_counts.keys()):
                print(f"  Depth {depth}: {depth_counts[depth]} profiles")
    
    def export_to_csv(self, filename: str = None):
        """Export high-follower profiles to CSV"""
        
        if not filename:
            timestamp = int(time.time())
            filename = f"instagram_500_profiles_{timestamp}.csv"
        
        if not self.high_follower_profiles:
            print("❌ No profiles to export")
            return
        
        # Sort by followers descending
        sorted_profiles = sorted(self.high_follower_profiles, key=lambda x: x.followers, reverse=True)
        
        # Take only the top 500 if we have more
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
        
        print(f"\n💾 CSV Export Complete!")
        print(f"📁 File: {filename}")
        print(f"📊 Exported: {len(profiles_to_export)} profiles")
        print(f"👥 Follower range: {self._format_number(profiles_to_export[-1].followers)} - {self._format_number(profiles_to_export[0].followers)}")

def main():
    import os, sys
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        print("❌ Missing INSTAGRAM_API_KEY environment variable")
        sys.exit(1)
    
    # Get hashtag from command line or use default
    hashtag = sys.argv[1] if len(sys.argv) > 1 else "luxury"
    
    print("🚀 Instagram Iterative Discovery System")
    print("🎯 Goal: Find 500 profiles with 50,000+ followers")
    print("🔍 Method: BFS through hashtag → similar accounts → similar of similar")
    print(f"📝 Starting hashtag: #{hashtag}")
    print(f"💡 Usage: python3 {sys.argv[0]} <hashtag>")
    
    discovery = IterativeInstagramDiscovery(API_KEY)
    
    # Start discovery process
    profiles = discovery.discover_500_profiles(hashtag)
    
    # Export to CSV
    discovery.export_to_csv()
    
    print(f"\n✅ Discovery mission complete!")

if __name__ == "__main__":
    main() 