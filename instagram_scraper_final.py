#!/usr/bin/env python3
"""
Instagram Hashtag Profile Scraper - FINAL WORKING VERSION
Extracts user profiles from hashtag posts using the correct API structure
"""

import requests
import json
import sys
import time
import re
from typing import List, Dict, Optional

class InstagramScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
        }
    
    def search_hashtag(self, hashtag: str) -> Optional[List[Dict]]:
        """Search for profiles using hashtag posts"""
        
        clean_hashtag = hashtag.replace('#', '')
        print(f"🔍 Searching for profiles using hashtag: #{clean_hashtag}")
        
        endpoint = f"/search_hashtag.php?hashtag={clean_hashtag}"
        url = f"{self.base_url}{endpoint}"
        
        print(f"📡 Making request to: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Got response data")
                
                # Extract user profiles from the post data
                profiles = self._extract_users_from_posts(data)
                if profiles:
                    print(f"✅ Found {len(profiles)} unique user profiles")
                    return profiles
                else:
                    print("⚠️  No user profiles could be extracted")
                    return None
                    
            else:
                print(f"❌ Request failed with status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
    
    def _extract_users_from_posts(self, data: Dict) -> List[Dict]:
        """Extract user data from posts structure"""
        
        all_users = {}  # Use dict to avoid duplicates
        
        # Get posts from both regular and top posts
        posts_sources = []
        
        if 'posts' in data and isinstance(data['posts'], dict):
            posts_edges = data['posts'].get('edges', [])
            posts_sources.append(('posts', posts_edges))
            
        if 'top_posts' in data and isinstance(data['top_posts'], dict):
            top_posts_edges = data['top_posts'].get('edges', [])
            posts_sources.append(('top_posts', top_posts_edges))
        
        print(f"🔍 Processing posts from {len(posts_sources)} sources")
        
        for source_name, edges in posts_sources:
            print(f"📊 Processing {len(edges)} posts from {source_name}")
            
            for edge in edges:
                if not isinstance(edge, dict) or 'node' not in edge:
                    continue
                    
                node = edge['node']
                user_data = self._extract_user_from_post_node(node)
                
                if user_data and user_data.get('username'):
                    username = user_data['username']
                    if username not in all_users:
                        all_users[username] = user_data
                        print(f"👤 Found user: @{username}")
        
        return list(all_users.values())
    
    def _extract_user_from_post_node(self, node: Dict) -> Optional[Dict]:
        """Extract user information from a post node"""
        
        # Get user ID from owner
        user_id = None
        if 'owner' in node and isinstance(node['owner'], dict):
            user_id = node['owner'].get('id')
        
        # Extract username from accessibility caption
        username = None
        if 'accessibility_caption' in node:
            caption = node['accessibility_caption']
            username = self._extract_username_from_caption(caption)
        
        # Get post shortcode for profile URL construction
        shortcode = node.get('shortcode', '')
        
        if username:
            return {
                'user_id': user_id,
                'username': username,
                'shortcode': shortcode,
                'post_url': f"https://instagram.com/p/{shortcode}" if shortcode else None,
                'profile_url': f"https://instagram.com/{username}",
                'found_from': 'hashtag_search'
            }
        
        return None
    
    def _extract_username_from_caption(self, caption: str) -> Optional[str]:
        """Extract username from accessibility caption"""
        
        if not caption:
            return None
            
        # Pattern: "Photo shared by USERNAME on..."
        # Pattern: "Video shared by USERNAME on..."
        # Pattern: "Reel shared by USERNAME on..."
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
                # Validate username format
                if re.match(r'^[a-zA-Z0-9_.]+$', username) and len(username) <= 30:
                    return username
        
        return None
    
    def format_profile_data(self, profiles: List[Dict]) -> List[Dict]:
        """Format profiles for output (limited data available)"""
        
        formatted_profiles = []
        
        for profile in profiles:
            try:
                formatted_profile = {
                    'username': profile.get('username', 'Unknown'),
                    'full_name': '',  # Not available from this API
                    'followers': 0,   # Not available from this API
                    'following': 0,   # Not available from this API
                    'posts': 0,       # Not available from this API
                    'verified': False, # Not available from this API
                    'profile_url': profile.get('profile_url', ''),
                    'biography': '',   # Not available from this API
                    'user_id': profile.get('user_id', ''),
                    'sample_post_url': profile.get('post_url', ''),
                    'data_source': 'Instagram Hashtag Search API'
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
        print("⚠️  Note: This API provides limited profile data (usernames only)")
        print("   For full profile data, additional API calls would be needed")
        print("=" * 80)
        
        for i, profile in enumerate(profiles, 1):
            print(f"\n{i:2d}. @{profile['username']}")
            print(f"    Profile URL: {profile['profile_url']}")
            if profile.get('sample_post_url'):
                print(f"    Sample Post: {profile['sample_post_url']}")
            if profile.get('user_id'):
                print(f"    User ID: {profile['user_id']}")
    
    def save_to_json(self, profiles: List[Dict], hashtag: str):
        """Save results to JSON file"""
        
        timestamp = int(time.time())
        filename = f"instagram_profiles_{hashtag}_{timestamp}.json"
        
        data = {
            'hashtag': hashtag,
            'search_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_profiles': len(profiles),
            'api_endpoint': '/search_hashtag.php',
            'data_limitations': 'This API provides limited profile data. Only usernames and user IDs are available.',
            'profiles': profiles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Results saved to {filename}")

def main():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        print("❌ Missing INSTAGRAM_API_KEY environment variable")
        sys.exit(1)
    
    # Get hashtag from command line or use default
    if len(sys.argv) > 1:
        hashtag = sys.argv[1]
    else:
        hashtag = "luxury"
    
    print("🚀 Instagram Hashtag Profile Scraper - FINAL VERSION")
    print(f"🔑 Using RapidAPI Instagram Scraper Stable API")
    print(f"🔍 Searching hashtag: #{hashtag}")
    
    scraper = InstagramScraper(API_KEY)
    
    # Search for profiles
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
            print(f"\n💡 To get full profile data (followers, bio, etc.), you would need:")
            print(f"   1. An API that provides detailed profile information")
            print(f"   2. Or make additional API calls for each username found")
        else:
            print(f"\n⚠️  No valid profile data could be extracted")
    else:
        print(f"\n❌ Failed to get data for hashtag #{hashtag}")
        print(f"💡 Try different hashtags like: travel, fashion, fitness, food")

if __name__ == "__main__":
    main() 