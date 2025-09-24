#!/usr/bin/env python3
"""
Test different Instagram profile API endpoints to find the correct one
"""

import requests
import json

def test_profile_endpoints():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    # Test username - try a simple one first
    test_username = "luxury.dubai.2025"  # One we found from hashtag search
    
    # Different possible endpoint formats
    endpoints_to_try = [
        f"/user_info.php?username={test_username}",
        f"/profile.php?username={test_username}",
        f"/user.php?username={test_username}",
        f"/instagram_profile.php?username={test_username}",
        f"/profile?username={test_username}",
        f"/user?username={test_username}",
        f"/userinfo?username={test_username}",
        f"/api/user?username={test_username}",
        f"/api/profile?username={test_username}",
        f"/v1/user?username={test_username}",
        f"/get_user?username={test_username}",
        f"/user_details.php?username={test_username}",
    ]
    
    print(f"🔍 Testing profile endpoints for username: {test_username}")
    print("=" * 60)
    
    for endpoint in endpoints_to_try:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testing: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ SUCCESS! Got JSON response")
                    print(f"📄 Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Look for follower-related fields
                    if isinstance(data, dict):
                        follower_fields = ['follower_count', 'followers', 'follower_num', 'subscribers']
                        found_followers = False
                        for field in follower_fields:
                            if field in data:
                                print(f"👥 Found {field}: {data[field]}")
                                found_followers = True
                        
                        if not found_followers:
                            print("⚠️  No follower count fields found")
                    
                    # Save successful response for analysis
                    filename = f"profile_response_{endpoint.replace('/', '_').replace('?', '_')}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"💾 Response saved to {filename}")
                    
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response")
                    print(f"📄 Raw response: {response.text[:200]}...")
                    
            elif response.status_code == 404:
                print(f"❌ Endpoint not found")
            elif response.status_code == 401:
                print(f"❌ Authentication failed")
            elif response.status_code == 429:
                print(f"❌ Rate limited")
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"📄 Response: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")

if __name__ == "__main__":
    test_profile_endpoints() 