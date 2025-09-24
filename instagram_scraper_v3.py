#!/usr/bin/env python3
"""
Instagram Hashtag Profile Scraper v3
Using the correct endpoint from RapidAPI documentation
Extracts user profiles from hashtag posts
"""

import requests
import json
import sys
import time
import os
from typing import List, Dict, Optional

class InstagramScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com',
            'Content-Type': 'application/json'
        }
    
    def search_hashtag(self, hashtag: str) -> Optional[List[Dict]]:
        """Search for profiles using the correct API endpoint"""
        
        clean_hashtag = hashtag.replace('#', '')
        print(f"🔍 Searching for profiles using hashtag: #{clean_hashtag}")
        
        # Use the correct endpoint format from RapidAPI docs
        endpoint = f"/search_hashtag.php?hashtag={clean_hashtag}"
        url = f"{self.base_url}{endpoint}"
        
        print(f"📡 Making request to: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success! Got response data")
                    print(f"📄 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Extract user profiles from posts
                    profiles = self._extract_user_profiles(data)
                    if profiles:
                        print(f"✅ Found {len(profiles)} unique user profiles")
                        return profiles
                    else:
                        print("⚠️  No user profile data found in response")
                        # Print first part of response for debugging
                        print(f"📄 Response sample: {str(data)[:500]}...")
                        return None
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"📄 Raw response: {response.text[:500]}...")
                    return None
                    
            elif response.status_code == 401:
                print("❌ Authentication failed - check API key")
                return None
            elif response.status_code == 429:
                print("⏳ Rate limit exceeded")
                return None
            elif response.status_code == 404:
                print("❌ Endpoint not found")
                return None
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
    
    def _extract_user_profiles(self, data: Dict) -> Optional[List[Dict]]:
        """Extract user profiles from hashtag posts data"""
        
        all_users = {}  # Use dict to avoid duplicates by username
        
        # Look for posts in different locations
        posts_sources = [
            data.get('posts', []),
            data.get('top_posts', []),
            data.get('recent_posts', []),
        ]
        
        # Also check nested structures
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    posts_sources.append(value)
                elif isinstance(value, dict):
                    # Check nested dictionaries for posts
                    posts_sources.extend([
                        value.get('posts', []),
                        value.get('top_posts', []),
                        value.get('recent_posts', []),
                        value.get('data', []),
                        value.get('edges', []),
                    ])
        
        print(f"🔍 Searching through {len(posts_sources)} potential post sources")
        
        for posts in posts_sources:
            if not isinstance(posts, list):
                continue
                
            print(f"📊 Checking posts list with {len(posts)} items")
            
            for post in posts:
                if not isinstance(post, dict):
                    continue
                
                # Extract user data from post
                user_data = self._extract_user_from_post(post)
                if user_data and user_data.get('username'):
                    username = user_data['username']
                    if username not in all_users:
                        all_users[username] = user_data
                        print(f"👤 Found user: @{username}")
        
        if all_users:
            return list(all_users.values())
        
        print("🔍 No users found, let's explore the data structure...")
        self._debug_data_structure(data)
        return None
    
    def _extract_user_from_post(self, post: Dict) -> Optional[Dict]:
        """Extract user information from a single post"""
        
        # Look for user data in different locations within a post
        user_sources = [
            post.get('user'),
            post.get('owner'),
            post.get('author'),
            post.get('profile'),
            post.get('account'),
            post,  # Sometimes user data is at post level
        ]
        
        # Also check nested node structures (common in Instagram APIs)
        if 'node' in post:
            node = post['node']
            user_sources.extend([
                node.get('user'),
                node.get('owner'),
                node.get('author'),
                node,
            ])
        
        for user_data in user_sources:
            if not isinstance(user_data, dict):
                continue
                
            # Check if this looks like user data
            if self._is_user_data(user_data):
                return user_data
        
        return None
    
    def _is_user_data(self, item: Dict) -> bool:
        """Check if item contains user-like data"""
        if not isinstance(item, dict):
            return False
            
        # Must have username and at least one other user field
        has_username = any(field in item for field in ['username', 'user_name', 'handle'])
        
        user_fields = [
            'follower_count', 'followers', 'follower_num', 'followers_count',
            'profile_pic_url', 'avatar', 'profile_picture', 'profile_img',
            'is_verified', 'verified', 'is_private', 'private',
            'full_name', 'name', 'display_name', 'biography', 'bio'
        ]
        
        has_user_field = any(field in item for field in user_fields)
        
        return has_username and has_user_field
    
    def _debug_data_structure(self, data: Dict, max_depth: int = 3, current_depth: int = 0):
        """Debug helper to understand the data structure"""
        
        if current_depth >= max_depth:
            return
            
        indent = "  " * current_depth
        
        if isinstance(data, dict):
            print(f"{indent}📁 Dict with keys: {list(data.keys())}")
            for key, value in list(data.items())[:5]:  # Show first 5 keys
                print(f"{indent}  🔑 {key}: {type(value)}")
                if isinstance(value, (dict, list)) and len(str(value)) < 200:
                    self._debug_data_structure(value, max_depth, current_depth + 1)
        elif isinstance(data, list):
            print(f"{indent}📋 List with {len(data)} items")
            if data and len(data) > 0:
                print(f"{indent}  📄 First item type: {type(data[0])}")
                if isinstance(data[0], dict):
                    print(f"{indent}  📄 First item keys: {list(data[0].keys())}")
    
    def format_profile_data(self, profiles: List[Dict]) -> List[Dict]:
        """Format and standardize profile data"""
        formatted_profiles = []
        
        for profile in profiles:
            try:
                # Handle different field name variations
                username = (profile.get('username') or 
                           profile.get('user_name') or 
                           profile.get('handle') or 
                           profile.get('account_name') or 
                           'Unknown')
                
                full_name = (profile.get('full_name') or 
                            profile.get('name') or 
                            profile.get('display_name') or 
                            '')
                
                followers = (profile.get('follower_count') or 
                            profile.get('followers') or 
                            profile.get('followers_count') or 
                            profile.get('follower_num') or 0)
                
                following = (profile.get('following_count') or 
                            profile.get('following') or 
                            profile.get('follows') or 0)
                
                posts = (profile.get('media_count') or 
                        profile.get('posts') or 
                        profile.get('post_count') or 0)
                
                verified = (profile.get('is_verified') or 
                           profile.get('verified') or False)
                
                bio = (profile.get('biography') or 
                      profile.get('bio') or 
                      profile.get('description') or '')
                
                formatted_profile = {
                    'username': username,
                    'full_name': full_name,
                    'followers': int(followers) if str(followers).isdigit() else 0,
                    'following': int(following) if str(following).isdigit() else 0,
                    'posts': int(posts) if str(posts).isdigit() else 0,
                    'verified': bool(verified),
                    'profile_url': f"https://instagram.com/{username}",
                    'biography': bio[:100] + ('...' if len(bio) > 100 else '')
                }
                
                formatted_profiles.append(formatted_profile)
                
            except Exception as e:
                print(f"⚠️  Error formatting profile: {e}")
                continue
                
        return formatted_profiles
    
    def print_results(self, profiles: List[Dict], hashtag: str):
        """Print formatted results to console"""
        
        if not profiles:
            print(f"\n❌ No profiles found for hashtag #{hashtag}")
            return
        
        print(f"\n🎯 Found {len(profiles)} unique profiles for #{hashtag}")
        print("=" * 80)
        
        # Sort by follower count (descending)
        sorted_profiles = sorted(profiles, key=lambda x: x['followers'], reverse=True)
        
        for i, profile in enumerate(sorted_profiles, 1):
            verified_icon = " ✓" if profile['verified'] else ""
            followers_formatted = self._format_number(profile['followers'])
            following_formatted = self._format_number(profile['following'])
            posts_formatted = self._format_number(profile['posts'])
            
            print(f"\n{i:2d}. @{profile['username']}{verified_icon}")
            if profile['full_name']:
                print(f"    Name: {profile['full_name']}")
            print(f"    Followers: {followers_formatted}")
            print(f"    Following: {following_formatted}")
            print(f"    Posts: {posts_formatted}")
            print(f"    URL: {profile['profile_url']}")
            if profile['biography']:
                print(f"    Bio: {profile['biography']}")
    
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
    
    def save_to_json(self, profiles: List[Dict], hashtag: str):
        """Save results to JSON file"""
        
        timestamp = int(time.time())
        filename = f"instagram_profiles_{hashtag}_{timestamp}.json"
        
        data = {
            'hashtag': hashtag,
            'search_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_profiles': len(profiles),
            'api_endpoint': '/search_hashtag.php',
            'profiles': profiles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Results saved to {filename}")

def main():
    api_key = os.getenv("INSTAGRAM_API_KEY")
    if not api_key:
        print("❌ Missing INSTAGRAM_API_KEY environment variable")
        sys.exit(1)
    
    # Get hashtag from command line or use default
    if len(sys.argv) > 1:
        hashtag = sys.argv[1]
    else:
        hashtag = "luxury"
    
    print("🚀 Instagram Hashtag Profile Scraper v3")
    print(f"🔑 Using correct API endpoint from RapidAPI docs")
    print(f"🔍 Searching hashtag: #{hashtag}")
    
    scraper = InstagramScraper(api_key)
    
    # Search for profiles using correct endpoint
    profiles_data = scraper.search_hashtag(hashtag)
    
    if profiles_data:
        # Format the data
        formatted_profiles = scraper.format_profile_data(profiles_data)
        
        if formatted_profiles:
            # Print results
            scraper.print_results(formatted_profiles, hashtag)
            
            # Save to JSON file
            scraper.save_to_json(formatted_profiles, hashtag)
            
            print(f"\n✅ Search completed successfully!")
            print(f"📊 Summary: Found {len(formatted_profiles)} profiles for #{hashtag}")
        else:
            print(f"\n⚠️  No valid profile data could be extracted")
    else:
        print(f"\n❌ Failed to get data for hashtag #{hashtag}")

if __name__ == "__main__":
    main() 