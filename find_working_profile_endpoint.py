#!/usr/bin/env python3
"""
Find the working profile endpoint that returns the user_data structure with follower_count
"""

import requests
import json

def test_profile_endpoint_variations():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    # Test with MrBeast since we know the expected response
    test_username = "mrbeast"
    
    # Common endpoint patterns for user profile data
    endpoints_to_try = [
        f"/get_user_info.php?username={test_username}",
        f"/user_profile.php?username={test_username}",
        f"/profile_data.php?username={test_username}",
        f"/user_details.php?username={test_username}",
        f"/instagram_user.php?username={test_username}",
        f"/user_info_full.php?username={test_username}",
        f"/profile_complete.php?username={test_username}",
        f"/user_data.php?username={test_username}",
        f"/profile.php?user={test_username}",
        f"/user.php?user={test_username}",
        f"/get_profile.php?username={test_username}",
    ]
    
    print(f"🔍 Testing profile endpoints for @{test_username}")
    print(f"🎯 Looking for response with 'user_data' and 'follower_count'")
    print("=" * 70)
    
    for endpoint in endpoints_to_try:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testing: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ SUCCESS! Got JSON response")
                    
                    # Check if this matches the expected structure
                    if isinstance(data, dict) and 'user_data' in data:
                        user_data = data['user_data']
                        if 'follower_count' in user_data:
                            follower_count = user_data['follower_count']
                            username = user_data.get('username', 'Unknown')
                            print(f"🎉 PERFECT MATCH! Found the working endpoint!")
                            print(f"👤 Username: @{username}")
                            print(f"👥 Followers: {follower_count:,}")
                            print(f"👣 Following: {user_data.get('following_count', 0):,}")
                            print(f"📸 Posts: {user_data.get('media_count', 0):,}")
                            print(f"✓ Verified: {user_data.get('is_verified', False)}")
                            
                            # Save the working response
                            filename = f"working_profile_endpoint_response.json"
                            with open(filename, 'w') as f:
                                json.dump(data, f, indent=2)
                            print(f"💾 Working response saved to {filename}")
                            
                            return endpoint  # Return the working endpoint
                    
                    # If not exact match, check for any follower-related fields
                    else:
                        print(f"📄 Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        
                        # Look for follower data anywhere in the response
                        if isinstance(data, dict):
                            def find_follower_data(obj, path=""):
                                results = []
                                if isinstance(obj, dict):
                                    for key, value in obj.items():
                                        current_path = f"{path}.{key}" if path else key
                                        if 'follower' in key.lower():
                                            results.append(f"{current_path}: {value}")
                                        if isinstance(value, (dict, list)):
                                            results.extend(find_follower_data(value, current_path))
                                elif isinstance(obj, list):
                                    for i, item in enumerate(obj):
                                        current_path = f"{path}[{i}]"
                                        results.extend(find_follower_data(item, current_path))
                                return results
                            
                            follower_fields = find_follower_data(data)
                            if follower_fields:
                                print(f"👥 Found follower fields: {follower_fields}")
                            else:
                                print(f"⚠️  No follower data found in response")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"📄 Raw response: {response.text[:200]}...")
                    
            elif response.status_code == 404:
                print(f"❌ Endpoint not found")
            elif response.status_code == 429:
                print(f"⏳ Rate limited")
            else:
                print(f"❌ Status {response.status_code}: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
    
    print(f"\n❌ No working endpoint found yet")
    return None

if __name__ == "__main__":
    working_endpoint = test_profile_endpoint_variations()
    if working_endpoint:
        print(f"\n🎉 WORKING ENDPOINT: {working_endpoint}")
        print(f"📋 Use this pattern: /path?username={{username}}")
    else:
        print(f"\n💭 The working endpoint might use a different parameter name or URL structure")
        print(f"🔍 Try checking the RapidAPI documentation for the exact format") 