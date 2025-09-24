#!/usr/bin/env python3
"""
Instagram Hashtag Profile Scraper v2
Searches Instagram profiles by hashtag with fallback to demo data
"""

import requests
import json
import sys
import time
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
        """Search for profiles using a specific hashtag"""
        
        clean_hashtag = hashtag.replace('#', '')
        print(f"🔍 Searching for profiles using hashtag: #{clean_hashtag}")
        
        # Try various common Instagram API endpoint patterns
        endpoints_to_try = [
            # Standard patterns
            f"/hashtag/{clean_hashtag}",
            f"/hashtag/{clean_hashtag}/top",
            f"/hashtag/{clean_hashtag}/recent", 
            f"/tag/{clean_hashtag}",
            f"/tags/{clean_hashtag}",
            
            # Query parameter patterns
            f"/hashtag?tag={clean_hashtag}",
            f"/search/hashtag?q={clean_hashtag}",
            f"/search?hashtag={clean_hashtag}",
            f"/explore/tags/{clean_hashtag}",
            
            # API versioning patterns
            f"/v1/hashtag/{clean_hashtag}",
            f"/v1/tags/{clean_hashtag}",
            f"/api/hashtag/{clean_hashtag}",
            f"/api/v1/hashtag/{clean_hashtag}",
            
            # Instagram-specific patterns
            f"/ig/hashtag/{clean_hashtag}",
            f"/instagram/hashtag/{clean_hashtag}",
            f"/insta/hashtag/{clean_hashtag}",
        ]
        
        for endpoint in endpoints_to_try:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"📡 Trying: {endpoint}")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Success with {endpoint}!")
                    profiles = self._extract_profiles(data)
                    if profiles:
                        return profiles
                        
                elif response.status_code == 401:
                    print("❌ Authentication failed - API key issue")
                    break
                elif response.status_code == 429:
                    print("⏳ Rate limited - waiting...")
                    time.sleep(5)
                elif response.status_code == 404:
                    continue  # Try next endpoint
                else:
                    print(f"⚠️  Status {response.status_code}: {response.text[:100]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Network error: {str(e)[:50]}")
                continue
        
        print("❌ No working endpoints found")
        return None
    
    def _extract_profiles(self, data: Dict) -> Optional[List[Dict]]:
        """Extract profile data from API response"""
        
        # Handle different response structures
        possible_paths = [
            data,  # Direct array
            data.get('profiles', []),
            data.get('data', {}).get('profiles', []),
            data.get('items', []),
            data.get('results', []),
            data.get('users', []),
            data.get('accounts', []),
        ]
        
        for profiles in possible_paths:
            if isinstance(profiles, list) and len(profiles) > 0:
                # Check if this looks like profile data
                first_item = profiles[0]
                if self._is_profile_data(first_item):
                    print(f"✅ Found {len(profiles)} profiles in response")
                    return profiles
        
        print("⚠️  No recognizable profile data found")
        return None
    
    def _is_profile_data(self, item: Dict) -> bool:
        """Check if item contains profile-like data"""
        profile_fields = [
            'username', 'user_name', 'handle', 'account_name',
            'follower_count', 'followers', 'follower_num',
            'profile_pic_url', 'avatar', 'profile_picture'
        ]
        return any(field in item for field in profile_fields)
    
    def get_demo_data(self, hashtag: str) -> List[Dict]:
        """Generate realistic demo data for the hashtag"""
        
        # Demo profiles based on hashtag
        luxury_profiles = [
            {
                'username': 'chanel',
                'full_name': 'CHANEL',
                'follower_count': 52000000,
                'following_count': 123,
                'media_count': 3420,
                'is_verified': True,
                'biography': 'French luxury fashion house founded in 1910 by Gabrielle "Coco" Chanel.'
            },
            {
                'username': 'louisvuitton',
                'full_name': 'Louis Vuitton',
                'follower_count': 46000000,
                'following_count': 142,
                'media_count': 4156,
                'is_verified': True,
                'biography': 'Luxury French fashion and leather goods company since 1854.'
            },
            {
                'username': 'gucci',
                'full_name': 'Gucci',
                'follower_count': 48000000,
                'following_count': 98,
                'media_count': 2987,
                'is_verified': True,
                'biography': 'Italian luxury fashion house founded in Florence in 1921.'
            },
            {
                'username': 'rolex',
                'full_name': 'Rolex',
                'follower_count': 12000000,
                'following_count': 0,
                'media_count': 1234,
                'is_verified': True,
                'biography': 'Swiss luxury watch manufacturer. A crown for every achievement.'
            },
            {
                'username': 'luxurylifestyle',
                'full_name': 'Luxury Lifestyle',
                'follower_count': 2400000,
                'following_count': 892,
                'media_count': 5678,
                'is_verified': False,
                'biography': 'Showcasing the finest in luxury living, fashion, and travel.'
            }
        ]
        
        travel_profiles = [
            {
                'username': 'natgeotravel',
                'full_name': 'National Geographic Travel',
                'follower_count': 24000000,
                'following_count': 567,
                'media_count': 8765,
                'is_verified': True,
                'biography': 'Official travel account of National Geographic.'
            },
            {
                'username': 'beautifuldestinations',
                'full_name': 'Beautiful Destinations',
                'follower_count': 16000000,
                'following_count': 2134,
                'media_count': 12000,
                'is_verified': True,
                'biography': 'The most beautiful places on Earth 🌍'
            }
        ]
        
        fashion_profiles = [
            {
                'username': 'vogue',
                'full_name': 'Vogue',
                'follower_count': 30000000,
                'following_count': 3456,
                'media_count': 15678,
                'is_verified': True,
                'biography': 'The worlds most influential fashion magazine.'
            }
        ]
        
        # Select profiles based on hashtag
        if hashtag.lower() in ['luxury', 'luxe', 'expensive']:
            return luxury_profiles
        elif hashtag.lower() in ['travel', 'vacation', 'wanderlust']:
            return travel_profiles
        elif hashtag.lower() in ['fashion', 'style', 'ootd']:
            return fashion_profiles
        else:
            # Mix of all for unknown hashtags
            return luxury_profiles[:3] + travel_profiles[:1] + fashion_profiles[:1]
    
    def format_profile_data(self, profiles: List[Dict]) -> List[Dict]:
        """Format and standardize profile data"""
        formatted_profiles = []
        
        for profile in profiles:
            try:
                formatted_profile = {
                    'username': profile.get('username') or profile.get('user_name', 'Unknown'),
                    'full_name': profile.get('full_name') or profile.get('name', ''),
                    'followers': profile.get('follower_count') or profile.get('followers', 0),
                    'following': profile.get('following_count') or profile.get('following', 0),
                    'posts': profile.get('media_count') or profile.get('posts', 0),
                    'verified': profile.get('is_verified', False),
                    'profile_url': f"https://instagram.com/{profile.get('username', '')}",
                    'biography': (profile.get('biography', '') or profile.get('bio', ''))[:100]
                }
                
                # Add '...' if bio was truncated
                if len(profile.get('biography', '')) > 100:
                    formatted_profile['biography'] += '...'
                    
                formatted_profiles.append(formatted_profile)
                
            except Exception as e:
                print(f"⚠️  Error formatting profile: {e}")
                continue
                
        return formatted_profiles
    
    def print_results(self, profiles: List[Dict], hashtag: str, is_demo: bool = False):
        """Print formatted results to console"""
        
        if not profiles:
            print(f"\n❌ No profiles found for hashtag #{hashtag}")
            return
        
        demo_notice = " (DEMO DATA)" if is_demo else ""
        print(f"\n🎯 Found {len(profiles)} profiles for #{hashtag}{demo_notice}")
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
    
    def save_to_json(self, profiles: List[Dict], hashtag: str, is_demo: bool = False):
        """Save results to JSON file"""
        
        timestamp = int(time.time())
        filename = f"instagram_profiles_{hashtag}_{timestamp}.json"
        
        data = {
            'hashtag': hashtag,
            'search_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_profiles': len(profiles),
            'is_demo_data': is_demo,
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
    
    print("🚀 Instagram Hashtag Profile Scraper v2")
    print(f"🔑 API Key: {API_KEY[:10]}...")
    print(f"🔍 Searching hashtag: #{hashtag}")
    
    scraper = InstagramScraper(API_KEY)
    
    # Try real API first
    print("\n📡 Attempting to connect to Instagram API...")
    profiles_data = scraper.search_hashtag(hashtag)
    
    is_demo = False
    if not profiles_data:
        print("\n⚠️  API search failed, using demo data to show functionality...")
        profiles_data = scraper.get_demo_data(hashtag)
        is_demo = True
    
    if profiles_data:
        # Format the data
        formatted_profiles = scraper.format_profile_data(profiles_data)
        
        # Print results
        scraper.print_results(formatted_profiles, hashtag, is_demo)
        
        # Save to JSON file
        scraper.save_to_json(formatted_profiles, hashtag, is_demo)
        
        if is_demo:
            print(f"\n💡 This demo shows what the script would do with real API data")
            print(f"📋 To test with other hashtags: python3 {sys.argv[0]} <hashtag>")
            print(f"📝 Try: travel, fashion, fitness, food, photography")
        else:
            print(f"\n✅ Search completed successfully with real API data!")
            
        print(f"📊 Summary: Found {len(formatted_profiles)} profiles for #{hashtag}")
        
    else:
        print(f"\n❌ Failed to get any data for #{hashtag}")

if __name__ == "__main__":
    main() 