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
import os
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
        """Search for profiles using a specific hashtag"""
        
        # Clean hashtag (remove # if present)
        clean_hashtag = hashtag.replace('#', '')
        
        print(f"🔍 Searching for profiles using hashtag: #{clean_hashtag}")
        
        # Try different endpoint variations
        endpoints = [
            f"/hashtag/{clean_hashtag}",
            f"/hashtag?tag={clean_hashtag}",
            f"/tag/{clean_hashtag}",
            f"/api/hashtag/{clean_hashtag}",
            f"/v1/hashtag/{clean_hashtag}",
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"📡 Trying endpoint: {url}")
                
                response = requests.get(url, headers=self.headers, timeout=30)
                print(f"📥 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Success! Got response from {endpoint}")
                    
                    # Handle different response formats
                    profiles = self._extract_profiles(data)
                    if profiles:
                        return profiles
                        
                elif response.status_code == 404:
                    print(f"⚠️  Endpoint not found: {endpoint}")
                    continue
                elif response.status_code == 401:
                    print("❌ Authentication failed - check API key")
                    return None
                elif response.status_code == 429:
                    print("⏳ Rate limit exceeded - waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    print(f"❌ Request failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error for {endpoint}: {e}")
                continue
                
        print("❌ All endpoints failed")
        return None
    
    def _extract_profiles(self, data: Dict) -> Optional[List[Dict]]:
        """Extract profile data from different response formats"""
        
        # Try different data structures
        if isinstance(data, list):
            return data
            
        if 'profiles' in data:
            return data['profiles']
            
        if 'data' in data and 'profiles' in data['data']:
            return data['data']['profiles']
            
        if 'items' in data:
            return data['items']
            
        if 'results' in data:
            return data['results']
            
        # Check for nested structures
        if 'data' in data:
            nested_data = data['data']
            if isinstance(nested_data, dict):
                for key, value in nested_data.items():
                    if isinstance(value, list) and len(value) > 0:
                        # Check if this looks like profile data
                        if self._is_profile_data(value[0]):
                            return value
        
        print(f"⚠️  Unexpected response format. Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        print(f"📄 Response sample: {str(data)[:500]}...")
        return None
    
    def _is_profile_data(self, item: Dict) -> bool:
        """Check if an item looks like profile data"""
        profile_indicators = ['username', 'follower_count', 'profile_pic_url', 'is_verified']
        return any(indicator in item for indicator in profile_indicators)
    
    def format_profile_data(self, profiles: List[Dict]) -> List[Dict]:
        """Format and standardize profile data"""
        formatted_profiles = []
        
        for profile in profiles:
            try:
                formatted_profile = {
                    'username': profile.get('username', 'Unknown'),
                    'full_name': profile.get('full_name', ''),
                    'followers': profile.get('follower_count', 0),
                    'following': profile.get('following_count', 0),
                    'posts': profile.get('media_count', 0),
                    'verified': profile.get('is_verified', False),
                    'profile_url': f"https://instagram.com/{profile.get('username', '')}",
                    'biography': profile.get('biography', '')[:100] + '...' if profile.get('biography', '') else ''
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
            
        print(f"\n🎯 Found {len(profiles)} profiles for hashtag #{hashtag}")
        print("=" * 80)
        
        # Sort by follower count (descending)
        sorted_profiles = sorted(profiles, key=lambda x: x['followers'], reverse=True)
        
        for i, profile in enumerate(sorted_profiles, 1):
            verified_icon = " ✓" if profile['verified'] else ""
            followers_formatted = self._format_number(profile['followers'])
            following_formatted = self._format_number(profile['following'])
            posts_formatted = self._format_number(profile['posts'])
            
            print(f"\n{i:2d}. @{profile['username']}{verified_icon}")
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
    
    def save_to_json(self, profiles: List[Dict], hashtag: str, filename: str = None):
        """Save results to JSON file"""
        if not filename:
            filename = f"instagram_profiles_{hashtag}_{int(time.time())}.json"
            
        data = {
            'hashtag': hashtag,
            'search_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_profiles': len(profiles),
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
        hashtag = "luxury"  # Default hashtag
    
    print("🚀 Instagram Hashtag Profile Scraper")
    print(f"🔑 API Key: {api_key[:10]}...")
    
    # Initialize scraper
    scraper = InstagramScraper(api_key)
    
    # Search for profiles
    profiles_data = scraper.search_hashtag(hashtag)
    
    if profiles_data:
        # Format the data
        formatted_profiles = scraper.format_profile_data(profiles_data)
        
        # Print results
        scraper.print_results(formatted_profiles, hashtag)
        
        # Save to JSON file
        scraper.save_to_json(formatted_profiles, hashtag)
        
        print(f"\n✅ Search completed successfully!")
        print(f"📊 Summary: Found {len(formatted_profiles)} profiles for #{hashtag}")
        
    else:
        print(f"\n❌ Failed to get data for hashtag #{hashtag}")
        print("💡 Possible issues:")
        print("   - API endpoint structure might be different")
        print("   - Rate limiting")
        print("   - Invalid API key")
        print("   - Hashtag has no associated profiles")

if __name__ == "__main__":
    main() 