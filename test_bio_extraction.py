#!/usr/bin/env python3
"""
Test bio extraction from Instagram profile API
"""

import requests
import json

def test_bio_extraction():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    # Test with profiles that likely have bios
    test_usernames = ["style", "marcus", "mom", "jessie"]  # From our luxury search
    
    for username in test_usernames:
        print(f"\n🔍 Testing bio extraction for @{username}")
        print("=" * 60)
        
        url = f"{base_url}/ig_get_fb_profile_hover.php?username_or_url={username}"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Got profile data for @{username}")
                
                # Save full response for analysis
                filename = f"profile_debug_{username}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"💾 Full response saved to {filename}")
                
                # Check user_data structure
                if 'user_data' in data:
                    user_data = data['user_data']
                    print(f"📊 User data keys: {list(user_data.keys())}")
                    
                    # Look for biography fields
                    bio_fields = ['biography', 'bio', 'description', 'about', 'bio_text']
                    found_bio = False
                    
                    for field in bio_fields:
                        if field in user_data:
                            bio_value = user_data[field]
                            print(f"📝 Found {field}: '{bio_value}'")
                            found_bio = True
                    
                    if not found_bio:
                        print(f"❌ No bio fields found in user_data")
                        
                        # Check nested structures
                        print(f"🔍 Checking for nested bio data...")
                        for key, value in user_data.items():
                            if isinstance(value, dict):
                                print(f"  📁 {key} contains: {list(value.keys())}")
                                for nested_key in value.keys():
                                    if 'bio' in nested_key.lower() or 'description' in nested_key.lower():
                                        print(f"    🎯 Found potential bio in {key}.{nested_key}: {value[nested_key]}")
                    
                    # Display current working data
                    print(f"\n📋 Current working data:")
                    print(f"   Username: {user_data.get('username', 'N/A')}")
                    print(f"   Full Name: {user_data.get('full_name', 'N/A')}")
                    print(f"   Followers: {user_data.get('follower_count', 0):,}")
                    print(f"   Following: {user_data.get('following_count', 0):,}")
                    print(f"   Posts: {user_data.get('media_count', 0):,}")
                    print(f"   Verified: {user_data.get('is_verified', False)}")
                    print(f"   Private: {user_data.get('is_private', False)}")
                    
                else:
                    print(f"❌ No user_data found in response")
                    print(f"📄 Response keys: {list(data.keys())}")
                    
            else:
                print(f"❌ Failed with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON error: {e}")

if __name__ == "__main__":
    test_bio_extraction() 