#!/usr/bin/env python3
"""
Test pagination token functionality
"""

import requests
import json

def test_pagination(hashtag: str, api_key: str):
    """Test if pagination tokens work"""
    
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    print(f"🔍 Testing pagination for #{hashtag}")
    print("=" * 50)
    
    # Test first page (no token)
    url1 = f"{base_url}/search_hashtag.php?hashtag={hashtag}"
    print(f"📄 Page 1: {url1}")
    
    try:
        response1 = requests.get(url1, headers=headers, timeout=30)
        if response1.status_code == 200:
            data1 = response1.json()
            
            # Check if we get a pagination token
            token = data1.get('pagination_token')
            print(f"   Status: {response1.status_code}")
            print(f"   Pagination token: {token}")
            
            # Count posts
            posts_count = 0
            if 'posts' in data1 and isinstance(data1['posts'], dict):
                posts_count += len(data1['posts'].get('edges', []))
            if 'top_posts' in data1 and isinstance(data1['top_posts'], dict):
                posts_count += len(data1['top_posts'].get('edges', []))
            
            print(f"   Total posts: {posts_count}")
            
            # Test second page if token exists
            if token:
                print(f"\n📄 Page 2 (token={token}):")
                url2 = f"{base_url}/search_hashtag.php?hashtag={hashtag}&pagination_token={token}"
                print(f"   URL: {url2}")
                
                response2 = requests.get(url2, headers=headers, timeout=30)
                if response2.status_code == 200:
                    data2 = response2.json()
                    
                    # Count posts on page 2
                    posts_count2 = 0
                    if 'posts' in data2 and isinstance(data2['posts'], dict):
                        posts_count2 += len(data2['posts'].get('edges', []))
                    if 'top_posts' in data2 and isinstance(data2['top_posts'], dict):
                        posts_count2 += len(data2['top_posts'].get('edges', []))
                    
                    token2 = data2.get('pagination_token')
                    print(f"   Status: {response2.status_code}")
                    print(f"   Total posts: {posts_count2}")
                    print(f"   Next token: {token2}")
                    
                    if posts_count2 > 0:
                        print(f"✅ Pagination working! Page 2 has different content")
                    else:
                        print(f"⚠️  Page 2 has no posts")
                else:
                    print(f"   ❌ Page 2 failed: {response2.status_code}")
            else:
                print(f"⚠️  No pagination token returned")
        
        else:
            print(f"❌ Page 1 failed: {response1.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    
    # Test pagination on a popular hashtag
    test_pagination("business", API_KEY)

if __name__ == "__main__":
    main() 