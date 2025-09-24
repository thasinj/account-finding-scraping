#!/usr/bin/env python3
"""
Test if we can resolve user IDs to usernames
"""

import requests
import json

def test_userid_resolution(api_key: str):
    """Test if we can convert user IDs to usernames"""
    
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    # Get some user IDs from hashtag search
    print("🔍 Getting user IDs from hashtag...")
    
    hashtag_url = f"{base_url}/search_hashtag.php?hashtag=gaming"
    response = requests.get(hashtag_url, headers=headers, timeout=30)
    
    user_ids = []
    if response.status_code == 200:
        data = response.json()
        
        if 'posts' in data and isinstance(data['posts'], dict):
            edges = data['posts'].get('edges', [])
            
            for edge in edges[:5]:  # Test first 5 user IDs
                if isinstance(edge, dict) and 'node' in edge:
                    node = edge['node']
                    if 'owner' in node and isinstance(node['owner'], dict):
                        user_id = node['owner'].get('id')
                        if user_id:
                            user_ids.append(user_id)
    
    print(f"📋 Found {len(user_ids)} user IDs: {user_ids}")
    
    # Now try to resolve these IDs to usernames
    print(f"\n🔄 Testing user ID resolution...")
    
    # Test various endpoints that might accept user ID
    endpoints_to_test = [
        "/ig_get_fb_profile_hover.php?username_or_url={}",
        "/user_info.php?user_id={}",
        "/profile.php?id={}",
        "/get_user_info.php?user_id={}",
    ]
    
    for user_id in user_ids[:3]:  # Test first 3 IDs
        print(f"\n👤 Testing user ID: {user_id}")
        
        for endpoint_pattern in endpoints_to_test:
            endpoint = endpoint_pattern.format(user_id)
            url = base_url + endpoint
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                print(f"  📡 {endpoint}: {response.status_code}", end="")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            # Look for username in response
                            username = None
                            if 'user_data' in data and isinstance(data['user_data'], dict):
                                username = data['user_data'].get('username')
                            elif 'username' in data:
                                username = data.get('username')
                            
                            if username:
                                print(f" ✅ → @{username}")
                                break
                            else:
                                print(f" ❌ (no username found)")
                        else:
                            print(f" ❌ (invalid JSON structure)")
                    except:
                        print(f" ❌ (JSON parse error)")
                else:
                    print(f" ❌")
                    
            except Exception as e:
                print(f"  📡 {endpoint}: ❌ {e}")
        
        print()

def main():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    
    print("🧪 Testing User ID → Username Resolution")
    print("=" * 60)
    
    test_userid_resolution(API_KEY)
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION:")
    print("If user ID resolution works → Use owner IDs (cleaner)")
    print("If user ID resolution fails → Stick with caption parsing (current working method)")

if __name__ == "__main__":
    main() 