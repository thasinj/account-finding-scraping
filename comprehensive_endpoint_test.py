#!/usr/bin/env python3
"""
Comprehensive test for Instagram profile endpoint with different patterns
"""

import requests
import json
import os

def test_comprehensive_endpoints():
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    test_username = "mrbeast"
    
    # Different parameter names and endpoint patterns
    endpoint_patterns = [
        # Basic patterns with different parameters
        ("/user_info.php", {"username": test_username}),
        ("/user_info.php", {"user": test_username}),
        ("/user_info.php", {"name": test_username}),
        ("/user_info.php", {"ig_username": test_username}),
        
        # Different endpoint names
        ("/profile_info.php", {"username": test_username}),
        ("/profile_info.php", {"user": test_username}),
        ("/get_user.php", {"username": test_username}),
        ("/get_user.php", {"user": test_username}),
        
        # Without .php extension
        ("/user_info", {"username": test_username}),
        ("/profile_info", {"username": test_username}),
        ("/user", {"username": test_username}),
        ("/profile", {"username": test_username}),
        
        # RESTful patterns
        (f"/user/{test_username}", {}),
        (f"/profile/{test_username}", {}),
        (f"/users/{test_username}", {}),
        
        # API versioned patterns
        ("/api/user", {"username": test_username}),
        ("/api/profile", {"username": test_username}),
        ("/v1/user", {"username": test_username}),
        ("/v1/profile", {"username": test_username}),
        
        # Instagram specific patterns
        ("/instagram_user_info.php", {"username": test_username}),
        ("/ig_user.php", {"username": test_username}),
        ("/insta_profile.php", {"username": test_username}),
        
        # Other possible patterns
        ("/userinfo.php", {"username": test_username}),
        ("/profiledata.php", {"username": test_username}),
        ("/user_profile_complete.php", {"username": test_username}),
    ]
    
    print(f"🔍 Comprehensive endpoint testing for @{test_username}")
    print(f"🎯 Looking for 'user_data' with 'follower_count': 76248832")
    print("=" * 80)
    
    for endpoint, params in endpoint_patterns:
        if params:
            # Build query string
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{base_url}{endpoint}?{query_string}"
            display_endpoint = f"{endpoint}?{query_string}"
        else:
            url = f"{base_url}{endpoint}"
            display_endpoint = endpoint
            
        print(f"\n📡 Testing: {display_endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Got JSON response")
                    print(f"📄 Keys: {list(data.keys())[:5]}" if isinstance(data, dict) else f"📄 Type: {type(data)}")
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON")
            elif response.status_code == 429:
                print(f"⏳ Rate limited")
                break
            else:
                print(f"❌ {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {str(e)[:50]}...")

if __name__ == "__main__":
    test_comprehensive_endpoints() 