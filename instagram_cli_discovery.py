#!/usr/bin/env python3
"""
Instagram CLI Discovery System - COMMAND LINE ARGUMENTS ONLY
🎯 Usage: python3 script.py --hashtag luxury --profiles 500 --min-followers 50000
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
import signal
from typing import List, Dict, Optional, Set, Deque
from collections import deque
from dataclasses import dataclass
import os

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

class CLIInstagramDiscovery:
    def __init__(self, api_key: str, target_profiles: int = 100, min_followers: int = 50000):
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
        self.hashtag_pagination_token = None  # Dedicated for hashtag pagination only
        
        # Graceful shutdown handling
        self.shutdown_requested = False
        self.current_hashtag = ""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Fixed configuration - ADAPTIVE DEPTH CONTROL
        self.LOW_QUALITY_MAX_DEPTH = 1   # Only 1 round for profiles that don't meet criteria
        self.HIGH_QUALITY_MAX_DEPTH = 3  # 3 rounds for profiles that meet our criteria
        self.SIMILAR_ACCOUNTS_PER_USER = 15  # Base amount for regular profiles
        self.HIGH_QUALITY_SIMILAR_ACCOUNTS = 25  # More expansion for successful profiles
        self.LOW_QUALITY_SIMILAR_ACCOUNTS = 8   # Less expansion for borderline profiles
        self.MAX_QUEUE_SIZE = 1000  # Prevent queue explosion
        self.INITIAL_HASHTAG_PAGES = 3
        self.MAX_HASHTAG_PAGES = 15  # Maximum pages we'll ever search
        self.current_hashtag_pages_searched = 0
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C and other termination signals gracefully"""
        print(f"\n\n⚠️  GRACEFUL SHUTDOWN REQUESTED (Signal {signum})")
        print(f"📊 Current progress: {len(self.high_follower_profiles)}/{self.TARGET_PROFILES} profiles found")
        print(f"💾 Saving current progress...")
        
        self.shutdown_requested = True
        
        # Save current progress immediately
        if self.high_follower_profiles:
            try:
                self._emergency_save()
                print(f"✅ Progress saved! Check the emergency CSV file.")
            except Exception as e:
                print(f"❌ Error saving progress: {e}")
        else:
            print(f"ℹ️  No profiles found yet to save.")
        
        print(f"🛑 Script will exit after current operation...")
    
    def _emergency_save(self):
        """Save current progress with emergency filename"""
        timestamp = int(time.time())
        min_k = self.MIN_FOLLOWERS // 1000
        emergency_file = f"EMERGENCY_instagram_{len(self.high_follower_profiles)}_profiles_{min_k}k+_{timestamp}.csv"
        
        self.export_to_csv(emergency_file)
        print(f"📁 Emergency save: {emergency_file}")
        
    def discover_profiles(self, hashtag: str) -> List[ProfileData]:
        """Discover profiles based on user criteria with DYNAMIC EXPANSION"""
        
        print(f"🚀 Instagram CLI Discovery")
        print(f"🎯 Target: {self.TARGET_PROFILES} profiles with {self.MIN_FOLLOWERS:,}+ followers")
        print(f"🔍 Hashtag: #{hashtag}")
        print(f"🧠 Adaptive BFS: {self.HIGH_QUALITY_MAX_DEPTH} rounds for successful profiles, {self.LOW_QUALITY_MAX_DEPTH} round for others")
        print(f"💡 Press Ctrl+C anytime to save progress and exit gracefully")
        print("=" * 80)
        
        self.current_hashtag = hashtag
        current_hashtag = hashtag
        expansion_round = 1
        
        try:
            while len(self.high_follower_profiles) < self.TARGET_PROFILES and expansion_round <= 3 and not self.shutdown_requested:
                
                print(f"\n🌱 SEED COLLECTION - Round {expansion_round}")
                
                if expansion_round == 1:
                    # Phase 1: Initial seed collection
                    print(f"🌱 COLLECTING INITIAL SEEDS from #{current_hashtag}")
                    seed_accounts = self._get_hashtag_seeds_initial(current_hashtag)
                else:
                    # Expand with more hashtag pages or try related hashtags
                    if self.current_hashtag_pages_searched < self.MAX_HASHTAG_PAGES:
                        print(f"🔄 EXPANDING HASHTAG PAGES for #{current_hashtag} (pages {self.current_hashtag_pages_searched + 1}-{min(self.current_hashtag_pages_searched + 5, self.MAX_HASHTAG_PAGES)})")
                        seed_accounts = self._expand_hashtag_seeds(current_hashtag)
                    else:
                        print(f"🔄 TRYING RELATED HASHTAGS (exhausted #{current_hashtag} pages)")
                        related = self._get_related_hashtags(current_hashtag)
                        seed_accounts = []
                        for alt_hashtag in related:
                            print(f"🔄 Trying #{alt_hashtag}...")
                            self.current_hashtag_pages_searched = 0  # Reset for new hashtag
                            seed_accounts = self._get_hashtag_seeds_initial(alt_hashtag)
                            if seed_accounts:
                                current_hashtag = alt_hashtag
                                break
                
                if not seed_accounts:
                    if expansion_round == 1:
                        print("❌ No initial seeds found! Trying related hashtags...")
                        related = self._get_related_hashtags(current_hashtag)
                        for alt_hashtag in related:
                            print(f"🔄 Trying #{alt_hashtag}...")
                            self.current_hashtag_pages_searched = 0
                            seed_accounts = self._get_hashtag_seeds_initial(alt_hashtag)
                            if seed_accounts:
                                current_hashtag = alt_hashtag
                                break
                    
                    if not seed_accounts:
                        print("❌ No seed accounts found even with related hashtags!")
                        if expansion_round == 1:
                            expansion_round += 1
                            continue
                        else:
                            break
                
                print(f"✅ Found {len(seed_accounts)} new seed accounts")
                
                # Phase 2: BFS expansion
                print(f"\n🔍 BFS EXPANSION - Round {expansion_round}")
                print(f"📊 Current progress: {len(self.high_follower_profiles)}/{self.TARGET_PROFILES} profiles")
                
                self._smart_bfs_discovery(seed_accounts)
                
                # Check for shutdown after BFS round
                if self.shutdown_requested:
                    break
                
                print(f"📊 After round {expansion_round}: {len(self.high_follower_profiles)}/{self.TARGET_PROFILES} profiles")
                
                if len(self.high_follower_profiles) >= self.TARGET_PROFILES:
                    print(f"🎉 TARGET REACHED! Found {len(self.high_follower_profiles)} profiles!")
                    break
                
                expansion_round += 1
        
        except KeyboardInterrupt:
            print(f"\n⚠️  Script interrupted by user!")
            
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print(f"💾 Saving current progress...")
            if self.high_follower_profiles:
                self._emergency_save()
        
        finally:
            # Phase 3: Results (always show final results)
            print(f"\n📊 FINAL RESULTS")
            self._print_summary()
        
        return self.high_follower_profiles
    
    def _get_related_hashtags(self, hashtag: str) -> List[str]:
        """Get related hashtags as fallbacks"""
        
        hashtag_families = {
            'luxury': ['fashion', 'lifestyle', 'style', 'designer'],
            'fashion': ['style', 'ootd', 'outfit', 'clothing'],
            'business': ['entrepreneur', 'startup', 'marketing', 'success'],
            'gaming': ['gamer', 'esports', 'videogames', 'streaming'],
            'fitness': ['gym', 'workout', 'health', 'bodybuilding'],
            'travel': ['vacation', 'adventure', 'explore', 'wanderlust'],
            'food': ['foodie', 'cooking', 'recipe', 'restaurant'],
            'tech': ['technology', 'coding', 'programming', 'startup']
        }
        
        for key, related in hashtag_families.items():
            if key in hashtag.lower():
                return related
        
        return ['lifestyle', 'style', 'business', 'success']
    
    def _get_hashtag_seeds_initial(self, hashtag: str) -> List[str]:
        """Get initial seed usernames from hashtag (first 3 pages)"""
        
        seed_usernames = []
        pagination_token = None
        
        pages_to_search = min(self.INITIAL_HASHTAG_PAGES, self.MAX_HASHTAG_PAGES)
        
        for page in range(1, pages_to_search + 1):
            page_usernames, next_token = self._search_hashtag_page(hashtag, pagination_token)
            seed_usernames.extend(page_usernames)
            
            print(f"  Page {page}: {len(page_usernames)} usernames")
            
            # Update pagination token for next page
            pagination_token = next_token
            self.current_hashtag_pages_searched = page
            
            # Store pagination token for potential expansion (dedicated to hashtag only)
            self.hashtag_pagination_token = next_token
            
            # Stop if no more pages
            if not pagination_token:
                break
                
            time.sleep(1)
        
        return list(set(seed_usernames))
    
    def _expand_hashtag_seeds(self, hashtag: str) -> List[str]:
        """Expand hashtag seed collection beyond initial pages"""
        
        seed_usernames = []
        pagination_token = self.hashtag_pagination_token
        
        if not pagination_token:
            print("  ❌ No hashtag pagination token available for expansion")
            print(f"  🔄 Current pages searched: {self.current_hashtag_pages_searched}")
            return []
        
        print(f"  🔄 Expanding from page {self.current_hashtag_pages_searched + 1} to {min(self.current_hashtag_pages_searched + 5, self.MAX_HASHTAG_PAGES)}")
        print(f"  🎫 Using pagination token: {pagination_token[:20]}..." if len(pagination_token) > 20 else f"  🎫 Using pagination token: {pagination_token}")
        
        # Search up to 5 more pages
        start_page = self.current_hashtag_pages_searched  # Don't modify this during loop
        max_expansion_pages = min(5, self.MAX_HASHTAG_PAGES - start_page)
        
        last_processed_page = start_page
        
        for page_offset in range(1, max_expansion_pages + 1):
            current_page_num = start_page + page_offset
            
            page_usernames, next_token = self._search_hashtag_page(hashtag, pagination_token)
            seed_usernames.extend(page_usernames)
            
            print(f"  Page {current_page_num}: {len(page_usernames)} usernames")
            
            # Update pagination token for next page  
            pagination_token = next_token
            self.hashtag_pagination_token = next_token
            last_processed_page = current_page_num
            
            # Stop if no more pages
            if not pagination_token:
                print(f"  ✅ Reached end of hashtag pages at page {current_page_num}")
                break
                
            time.sleep(1)
        
        # Update final page count after loop completes  
        self.current_hashtag_pages_searched = last_processed_page
        
        return list(set(seed_usernames))
    
    def _search_hashtag_page(self, hashtag: str, pagination_token: str = None) -> tuple:
        """Get usernames from hashtag page with pagination support"""
        
        clean_hashtag = hashtag.replace('#', '')
        
        # Build URL with pagination token if provided
        if pagination_token:
            url = f"{self.base_url}/search_hashtag.php?hashtag={clean_hashtag}&pagination_token={pagination_token}"
        else:
            url = f"{self.base_url}/search_hashtag.php?hashtag={clean_hashtag}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            self.total_api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                usernames = self._extract_usernames_from_posts(data)
                
                # Extract next pagination token
                next_token = data.get('pagination_token')
                
                return usernames, next_token
            else:
                return [], None
                
        except requests.exceptions.RequestException:
            return [], None
    
    def _extract_usernames_from_posts(self, data: Dict) -> List[str]:
        """Extract usernames from hashtag posts via caption parsing"""
        
        usernames = []
        
        # Get posts from both regular and top posts
        posts_sources = []
        if 'posts' in data and isinstance(data['posts'], dict):
            posts_edges = data['posts'].get('edges', [])
            posts_sources.append(posts_edges)
            
        if 'top_posts' in data and isinstance(data['top_posts'], dict):
            top_posts_edges = data['top_posts'].get('edges', [])
            posts_sources.append(top_posts_edges)
        
        for edges in posts_sources:
            for edge in edges:
                if isinstance(edge, dict) and 'node' in edge:
                    node = edge['node']
                    
                    if 'accessibility_caption' in node:
                        caption = node['accessibility_caption']
                        username = self._extract_username_from_caption(caption)
                        if username:
                            usernames.append(username)
        
        return list(set(usernames))
    
    def _extract_username_from_caption(self, caption: str) -> Optional[str]:
        """Extract username from accessibility caption with ENHANCED patterns"""
        
        if not caption:
            return None
        
        # 1. PRIORITY: Search for @username mentions anywhere in the caption (most reliable)
        # This captures explicit Instagram @mentions like @dailymillionairemind, @THEMULTIPASSIONATECLUB
        at_username_matches = re.findall(r'@([a-zA-Z0-9_.]+)', caption)
        for username in at_username_matches:
            if self._is_valid_username(username):
                return username
        
        # 2. Try "Photo/Video by X on" patterns, but extract FULL names and validate strictly
        patterns_for_photo_by = [
            r'Photo by ([a-zA-Z0-9_.\s]+) on',     # Captures "Jessica Chen" from "Photo by Jessica Chen on"
            r'Video by ([a-zA-Z0-9_.\s]+) on',
            r'Reel by ([a-zA-Z0-9_.\s]+) on',
            r'Photo shared by ([a-zA-Z0-9_.\s]+) on',
            r'Video shared by ([a-zA-Z0-9_.\s]+) on',
            r'Reel shared by ([a-zA-Z0-9_.\s]+) on',
            r'shared by ([a-zA-Z0-9_.\s]+) on',
            r'Photo shared by ([a-zA-Z0-9_.\s]+) tagging',
            r'by ([a-zA-Z0-9_.\s]+) in [A-Za-z]',
        ]
        
        for pattern in patterns_for_photo_by:
            match = re.search(pattern, caption, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                # CRITICAL: Only consider it a username if it's a SINGLE WORD (no spaces)
                # This prevents "Jessica Chen" from being considered a username
                if ' ' not in extracted_name and self._is_valid_username(extracted_name):
                    return extracted_name
        
        # 3. Fallback: Look for standalone usernames in quotes or other patterns
        # This catches patterns like 'User "username123" posted...'
        quote_patterns = [
            r'"([a-zA-Z0-9_.]+)"',
            r"'([a-zA-Z0-9_.]+)'",
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, caption)
            for username in matches:
                if self._is_valid_username(username):
                    return username
        
        return None
    
    def _is_valid_username(self, username: str) -> bool:
        """Check if username is valid with COMPREHENSIVE filtering"""
        if not username:
            return False
        
        # Instagram username rules: 1-30 chars, alphanumeric + dots + underscores
        if not re.match(r'^[a-zA-Z0-9_.]+$', username):
            return False
        
        if len(username) > 30 or len(username) < 1:
            return False
        
        # COMPREHENSIVE list of common false positives to filter out
        common_words = {
            # Social media terms
            'instagram', 'photo', 'video', 'image', 'picture', 'post', 'story', 'reel', 'igtv',
            'follow', 'like', 'share', 'tag', 'comment', 'dm', 'live', 'stories',
            
            # Generic terms that appear in captions
            'the', 'and', 'for', 'with', 'this', 'that', 'here', 'there', 'what', 'when',
            'where', 'how', 'why', 'who', 'all', 'any', 'can', 'now', 'new', 'get',
            
            # Common first names that show up in "Photo by [Name] on" patterns
            'john', 'jane', 'mike', 'sarah', 'david', 'emily', 'chris', 'alex', 'jessica',
            'michael', 'ashley', 'daniel', 'amanda', 'james', 'lisa', 'robert', 'jennifer',
            'william', 'elizabeth', 'richard', 'maria', 'thomas', 'susan', 'charles', 'nancy',
            
            # Time/date related (from "on July 27" etc)
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
            'september', 'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr',
            'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'monday', 'tuesday',
            'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            
            # Common caption words
            'content', 'creator', 'user', 'account', 'profile', 'page', 'feed', 'explore',
        }
        
        if username.lower() in common_words:
            return False
        
        # Additional checks for overly short usernames (likely fragments)
        if len(username) < 3:
            return False
        
        return True
    
    def _smart_bfs_discovery(self, seed_usernames: List[str]):
        """Smart BFS discovery"""
        
        # Initialize queue
        for username in seed_usernames:
            if username not in self.discovered_usernames:
                self.discovery_queue.append({
                    'username': username,
                    'depth': 0,
                    'parent': 'hashtag'
                })
                self.discovered_usernames.add(username)
        
        processed = 0
        found_count = 0
        banned_count = 0
        low_follower_count = 0
        high_quality_expansions = 0
        medium_quality_expansions = 0
        low_quality_expansions = 0
        
        while self.discovery_queue and len(self.high_follower_profiles) < self.TARGET_PROFILES and not self.shutdown_requested:
            current = self.discovery_queue.popleft()
            processed += 1
            
            username = current['username']
            depth = current['depth']
            
            # FREQUENT Progress indicator - show every 5 processed accounts
            if processed % 5 == 0 or processed == 1:
                progress = (len(self.high_follower_profiles) / self.TARGET_PROFILES) * 100
                queue_size = len(self.discovery_queue)
                print(f"  🔄 Processing @{username} (depth {depth}) | Progress: {progress:.1f}% | Found: {len(self.high_follower_profiles)}/{self.TARGET_PROFILES} | Queue: {queue_size}")
            
            # Get profile details with error handling
            try:
                profile_data = self._get_profile_details(username)
                
                if profile_data:
                    if profile_data.followers >= self.MIN_FOLLOWERS:
                        profile_data.discovery_path = f"depth_{depth}"
                        profile_data.discovery_depth = depth
                        self.high_follower_profiles.append(profile_data)
                        found_count += 1
                        
                        print(f"  ✅ Found #{found_count}: @{username} ({self._format_number(profile_data.followers)} followers)")
                        
                        # Periodic auto-save every 50 profiles
                        if len(self.high_follower_profiles) % 50 == 0:
                            try:
                                timestamp = int(time.time())
                                min_k = self.MIN_FOLLOWERS // 1000
                                auto_save_file = f"AUTO_SAVE_{len(self.high_follower_profiles)}_profiles_{min_k}k+_{timestamp}.csv"
                                self.export_to_csv(auto_save_file)
                                print(f"  💾 Auto-saved progress: {auto_save_file}")
                            except Exception as e:
                                print(f"  ⚠️  Auto-save failed: {e}")
                        
                        if len(self.high_follower_profiles) >= self.TARGET_PROFILES:
                            print(f"  🎯 TARGET REACHED! Found {len(self.high_follower_profiles)} profiles!")
                            break
                    else:
                        # Show rejections occasionally for transparency  
                        low_follower_count += 1
                        if processed % 10 == 0:
                            print(f"  ❌ Rejected @{username} ({self._format_number(profile_data.followers)} < {self._format_number(self.MIN_FOLLOWERS)})")
                    
                    # ADAPTIVE BFS: Different depth limits based on profile quality
                    progress_percent = (len(self.high_follower_profiles) / self.TARGET_PROFILES) * 100
                    
                    # Determine max depth based on profile quality
                    if profile_data.followers >= self.MIN_FOLLOWERS:
                        # HIGH QUALITY: Meets criteria → 3 rounds of BFS
                        max_depth_for_profile = self.HIGH_QUALITY_MAX_DEPTH
                        quality_tier = "HIGH-QUALITY"
                    else:
                        # LOW QUALITY: Doesn't meet criteria → 1 round only
                        max_depth_for_profile = self.LOW_QUALITY_MAX_DEPTH
                        quality_tier = "LOW-QUALITY"
                    
                    should_expand = (
                        depth < max_depth_for_profile and 
                        len(self.discovery_queue) < self.MAX_QUEUE_SIZE and
                        progress_percent < 80  # Stop expanding when 80% complete
                    )
                    
                    if should_expand:
                        try:
                            # ADAPTIVE EXPANSION based on profile quality
                            if profile_data.followers >= self.MIN_FOLLOWERS:
                                # HIGH QUALITY: Meets our criteria → More expansion + deeper BFS!
                                expansion_count = self.HIGH_QUALITY_SIMILAR_ACCOUNTS
                                expansion_type = f"HIGH-QUALITY(depth≤{self.HIGH_QUALITY_MAX_DEPTH})"
                                high_quality_expansions += 1
                            elif profile_data.followers >= self.MIN_FOLLOWERS * 0.5:  # 50% of threshold
                                # MEDIUM QUALITY: Close to threshold → Normal expansion, shallow BFS
                                expansion_count = self.SIMILAR_ACCOUNTS_PER_USER
                                expansion_type = f"MEDIUM-QUALITY(depth≤{self.LOW_QUALITY_MAX_DEPTH})"
                                medium_quality_expansions += 1
                            else:
                                # LOW QUALITY: Far below threshold → Minimal expansion + shallow BFS
                                expansion_count = self.LOW_QUALITY_SIMILAR_ACCOUNTS
                                expansion_type = f"LOW-QUALITY(depth≤{self.LOW_QUALITY_MAX_DEPTH})"
                                low_quality_expansions += 1
                            
                            similar_accounts = self._get_similar_accounts(username, expansion_count)
                            
                            added_count = 0
                            for similar in similar_accounts:
                                similar_username = similar.get('username')
                                if similar_username and similar_username not in self.discovered_usernames:
                                    self.discovery_queue.append({
                                        'username': similar_username,
                                        'depth': depth + 1,
                                        'parent': username
                                    })
                                    self.discovered_usernames.add(similar_username)
                                    added_count += 1
                                    
                                    # Stop adding if queue is getting too large
                                    if len(self.discovery_queue) >= self.MAX_QUEUE_SIZE:
                                        break
                            
                            if added_count > 0:
                                print(f"  📈 {expansion_type}: Added {added_count} similar accounts from @{username} ({self._format_number(profile_data.followers)} followers)")
                                
                        except Exception as e:
                            print(f"  ⚠️  Similar accounts failed for @{username}: {str(e)[:50]}")
                    else:
                        if processed % 15 == 0:
                            if len(self.discovery_queue) >= self.MAX_QUEUE_SIZE:
                                reason = "queue full"
                            elif progress_percent >= 80:
                                reason = "near target"
                            elif depth >= max_depth_for_profile:
                                reason = f"max depth {max_depth_for_profile} ({quality_tier})"
                            else:
                                reason = "unknown"
                            print(f"  🛑 Skipping expansion for @{username} ({reason})")
                else:
                    banned_count += 1
                    if processed % 10 == 0:
                        print(f"  ⚠️  Profile unavailable: @{username} (likely banned/private/suspended)")
                    # NO EXPANSION for banned/private accounts - they're dead ends
                        
            except Exception as e:
                print(f"  ❌ Network error for @{username}: {str(e)[:50]}")
            
            # OPTIMIZED: Much shorter sleep for faster processing
            time.sleep(0.05)  # Reduced from 0.2s → 0.05s (4x faster!)
        
        # Show statistics summary
        print(f"\n📊 BFS ROUND SUMMARY:")
        print(f"  🔄 Processed: {processed} accounts")
        print(f"  ✅ Found: {found_count} with {self.MIN_FOLLOWERS:,}+ followers")
        print(f"  ❌ Low followers: {low_follower_count} accounts")
        print(f"  ⚠️  Banned/Private: {banned_count} accounts")
        print(f"  📈 Expansions: {high_quality_expansions} high-quality (depth≤{self.HIGH_QUALITY_MAX_DEPTH}), {medium_quality_expansions} medium (depth≤{self.LOW_QUALITY_MAX_DEPTH}), {low_quality_expansions} low (depth≤{self.LOW_QUALITY_MAX_DEPTH})")
    
    def _get_profile_details(self, username: str) -> Optional[ProfileData]:
        """Get profile details with better error handling for banned/private accounts"""
        
        url = f"{self.base_url}/ig_get_fb_profile_hover.php?username_or_url={username}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=3)  # Reduced from 8s → 3s
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
    
    def _get_similar_accounts(self, username: str, max_accounts: int = 15) -> List[Dict]:
        """Get similar accounts - OPTIMIZED"""
        
        url = f"{self.base_url}/get_ig_similar_accounts.php?username_or_url={username}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=3)  # Reduced from 8s → 3s
            self.total_api_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    return [{'username': acc['username']} for acc in data[:max_accounts] 
                           if isinstance(acc, dict) and acc.get('username')]
            
            return []
            
        except requests.exceptions.RequestException:
            return []
    
    def _format_number(self, num: int) -> str:
        """Format numbers"""
        if num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)
    
    def _print_summary(self):
        """Print summary with enhanced stats"""
        
        print(f"📊 Found: {len(self.high_follower_profiles)} profiles")
        print(f"📞 API calls: {self.total_api_calls}")
        print(f"📄 Hashtag pages searched: {self.current_hashtag_pages_searched}")
        
        if self.high_follower_profiles:
            sorted_profiles = sorted(self.high_follower_profiles, key=lambda x: x.followers, reverse=True)
            
            print(f"\n🏆 Top 5:")
            for i, profile in enumerate(sorted_profiles[:5], 1):
                verified = " ✓" if profile.verified else ""
                print(f"  {i}. @{profile.username}{verified} - {self._format_number(profile.followers)} followers")
    
    def export_to_csv(self, output_file: str = None):
        """Export to CSV"""
        
        if not output_file:
            timestamp = int(time.time())
            min_k = self.MIN_FOLLOWERS // 1000
            output_file = f"instagram_{len(self.high_follower_profiles)}_profiles_{min_k}k+_{timestamp}.csv"
        
        if not self.high_follower_profiles:
            print("❌ No profiles to export")
            return
        
        sorted_profiles = sorted(self.high_follower_profiles, key=lambda x: x.followers, reverse=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'rank', 'username', 'full_name', 'followers', 'following', 'posts',
                'verified', 'private', 'profile_url', 'discovery_depth'
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
                    'discovery_depth': profile.discovery_depth
                })
        
        print(f"💾 Exported to: {output_file}")

def main():
    api_key = os.getenv("INSTAGRAM_API_KEY")
    if not api_key:
        print("❌ Missing INSTAGRAM_API_KEY environment variable")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='Instagram Profile Discovery - CLI Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 %(prog)s --hashtag luxury --profiles 100 --min-followers 50000
  python3 %(prog)s -t gaming -n 200 -f 25000 -o gaming_profiles.csv
  python3 %(prog)s -t fashion -n 50 -f 100000
        """
    )
    
    parser.add_argument('-t', '--hashtag', required=True,
                        help='Hashtag to search (without #)')
    parser.add_argument('-n', '--profiles', type=int, default=100,
                        help='Number of profiles to find (default: 100)')
    parser.add_argument('-f', '--min-followers', type=int, default=50000,
                        help='Minimum followers required (default: 50000)')
    parser.add_argument('-o', '--output', 
                        help='Output CSV file name (default: auto-generated)')
    
    args = parser.parse_args()
    
    print(f"🎯 Configuration:")
    print(f"   Hashtag: #{args.hashtag}")
    print(f"   Target: {args.profiles} profiles")
    print(f"   Min followers: {args.min_followers:,}")
    if args.output:
        print(f"   Output: {args.output}")
    
    # Start discovery
    discovery = CLIInstagramDiscovery(api_key, args.profiles, args.min_followers)
    profiles = discovery.discover_profiles(args.hashtag)
    discovery.export_to_csv(args.output)

if __name__ == "__main__":
    main() 