#!/usr/bin/env python3
"""
Debug script to examine Instagram API response structure
"""

import requests
import json

def debug_api_response():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    headers = {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    url = "https://instagram-scraper-stable-api.p.rapidapi.com/search_hashtag.php?hashtag=luxury"
    
    print("🔍 Making API request...")
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ API Response received!")
        print(f"📄 Top-level keys: {list(data.keys())}")
        
        # Examine posts structure more carefully
        if 'posts' in data:
            posts = data['posts']
            print(f"\n📊 Posts type: {type(posts)}")
            if isinstance(posts, dict):
                print(f"📊 Posts dict keys: {list(posts.keys())}")
                # Look for data in nested structures
                for key, value in posts.items():
                    print(f"  {key}: {type(value)} - {len(value) if isinstance(value, (list, dict)) else str(value)[:50]}")
            elif isinstance(posts, list):
                print(f"📊 Posts list length: {len(posts)}")
                if len(posts) > 0:
                    print("📄 First post structure:")
                    print(json.dumps(posts[0], indent=2)[:1000] + "...")
            else:
                print(f"📊 Posts content: {str(posts)[:200]}")
        
        # Examine top_posts structure  
        if 'top_posts' in data:
            top_posts = data['top_posts']
            print(f"\n⭐ Top posts type: {type(top_posts)}")
            if isinstance(top_posts, dict):
                print(f"⭐ Top posts dict keys: {list(top_posts.keys())}")
                for key, value in top_posts.items():
                    print(f"  {key}: {type(value)} - {len(value) if isinstance(value, (list, dict)) else str(value)[:50]}")
            elif isinstance(top_posts, list):
                print(f"⭐ Top posts list length: {len(top_posts)}")
                if len(top_posts) > 0:
                    print("📄 First top post structure:")
                    print(json.dumps(top_posts[0], indent=2)[:1000] + "...")
            else:
                print(f"⭐ Top posts content: {str(top_posts)[:200]}")
        
        # Save full response for analysis
        with open('instagram_api_response_debug.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Full response saved to instagram_api_response_debug.json")
        
        # Look for any user-like data in the structure
        print(f"\n🔍 Searching for user-related fields...")
        find_user_fields(data)
        
    else:
        print(f"❌ API request failed: {response.status_code}")
        print(f"Response: {response.text}")

def find_user_fields(data, path="", max_depth=5, current_depth=0):
    """Recursively find fields that might contain user data"""
    
    if current_depth >= max_depth:
        return
        
    user_indicators = [
        'username', 'user_name', 'handle', 'owner', 'author',
        'follower', 'following', 'verified', 'profile_pic', 
        'biography', 'bio', 'full_name', 'display_name'
    ]
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if this key indicates user data
            if any(indicator in key.lower() for indicator in user_indicators):
                print(f"👤 Found user field at {current_path}: {type(value)}")
                if isinstance(value, dict):
                    print(f"    Keys: {list(value.keys())[:10]}")
                elif isinstance(value, str) and len(value) < 100:
                    print(f"    Value: {value}")
                elif isinstance(value, list):
                    print(f"    List length: {len(value)}")
            
            # Recurse into nested structures
            if isinstance(value, (dict, list)) and current_depth < max_depth - 1:
                find_user_fields(value, current_path, max_depth, current_depth + 1)
                
    elif isinstance(data, list):
        # Check first few items in list
        for i, item in enumerate(data[:3]):
            if item is not None:  # Safety check
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                find_user_fields(item, current_path, max_depth, current_depth + 1)

if __name__ == "__main__":
    debug_api_response() 