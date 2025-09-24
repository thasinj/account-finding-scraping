#!/usr/bin/env python3
"""
Test the correct Instagram profile endpoint based on RapidAPI documentation
"""

import requests
import json

def test_profile_endpoint():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    # Try a well-known Instagram account
    test_usernames = ["nike", "instagram", "cristiano"]  # Famous accounts
    
    # Most likely endpoint patterns based on RapidAPI structure
    endpoints_to_try = [
        "/user_info.php?username={}",
        "/profile_info.php?username={}",
        "/get_user_info.php?username={}",
        "/user_profile.php?username={}",
    ]
    
    for username in test_usernames:
        print(f"\n🔍 Testing with username: @{username}")
        print("=" * 50)
        
        for endpoint_template in endpoints_to_try:
            endpoint = endpoint_template.format(username)
            url = f"{base_url}{endpoint}"
            
            print(f"📡 Testing: {endpoint}")
            
            try:
                response = requests.get(url, headers=headers, timeout=15)
                print(f"📥 Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ SUCCESS! Found working endpoint")
                        print(f"📄 Response type: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"📄 Keys: {list(data.keys())}")
                            
                            # Look for follower data
                            follower_fields = ['follower_count', 'followers', 'follower_num', 'edge_followed_by']
                            for field in follower_fields:
                                if field in data:
                                    print(f"👥 FOUND FOLLOWERS: {field} = {data[field]}")
                                    
                                    # Save the working response
                                    filename = f"working_profile_response_{username}.json"
                                    with open(filename, 'w') as f:
                                        json.dump(data, f, indent=2)
                                    print(f"💾 Working response saved to {filename}")
                                    
                                    return endpoint_template  # Return the working endpoint template
                        
                        elif isinstance(data, list) and len(data) > 0:
                            print(f"📄 List with {len(data)} items")
                            if isinstance(data[0], dict):
                                print(f"📄 First item keys: {list(data[0].keys())}")
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        print(f"📄 Raw response: {response.text[:200]}...")
                        
                elif response.status_code == 404:
                    print(f"❌ Endpoint not found")
                elif response.status_code == 429:
                    print(f"⏳ Rate limited - waiting...")
                    break  # Stop testing this username
                else:
                    print(f"❌ Status {response.status_code}: {response.text[:100]}...")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error: {e}")
        
        print("\n" + "="*50)
    
    print("\n❌ No working profile endpoint found")
    return None

if __name__ == "__main__":
    working_endpoint = test_profile_endpoint()
    if working_endpoint:
        print(f"\n🎉 WORKING ENDPOINT FOUND: {working_endpoint}")
    else:
        print(f"\n💡 Try checking the RapidAPI documentation for the exact endpoint format") 