#!/usr/bin/env python3
"""
Debug script to understand why hashtag search isn't finding usernames
"""

import requests
import json
import re
from typing import Optional

def debug_hashtag_search(hashtag: str, api_key: str):
    """Debug what the hashtag API returns"""
    
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    clean_hashtag = hashtag.replace('#', '')
    url = f"{base_url}/search_hashtag.php?hashtag={clean_hashtag}"
    
    print(f"🔍 Debugging hashtag: #{hashtag}")
    print(f"📡 URL: {url}")
    print("=" * 80)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📏 Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔍 Response Type: {type(data)}")
            
            # Save full response for inspection
            with open(f"hashtag_{hashtag}_debug.json", 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Saved full response to: hashtag_{hashtag}_debug.json")
            
            # Check top-level keys
            if isinstance(data, dict):
                print(f"\n📋 Top-level keys: {list(data.keys())}")
                
                # Check posts structure
                if 'posts' in data:
                    posts = data['posts']
                    print(f"📮 Posts type: {type(posts)}")
                    
                    if isinstance(posts, dict):
                        print(f"📮 Posts keys: {list(posts.keys())}")
                        
                        if 'edges' in posts:
                            edges = posts['edges']
                            print(f"📮 Posts edges count: {len(edges)}")
                            
                            # Look at first few posts
                            for i, edge in enumerate(edges[:3]):
                                print(f"\n🔍 Post {i+1}:")
                                if isinstance(edge, dict) and 'node' in edge:
                                    node = edge['node']
                                    print(f"  Node keys: {list(node.keys())}")
                                    
                                    if 'accessibility_caption' in node:
                                        caption = node['accessibility_caption']
                                        print(f"  Caption: {caption[:100]}...")
                                        
                                        # Try to extract username
                                        username = extract_username_from_caption(caption)
                                        if username:
                                            print(f"  ✅ Extracted username: @{username}")
                                        else:
                                            print(f"  ❌ No username found in caption")
                                    else:
                                        print(f"  ⚠️  No accessibility_caption in node")
                
                # Check top_posts structure
                if 'top_posts' in data:
                    top_posts = data['top_posts']
                    print(f"\n🏆 Top Posts type: {type(top_posts)}")
                    
                    if isinstance(top_posts, dict):
                        print(f"🏆 Top Posts keys: {list(top_posts.keys())}")
                        
                        if 'edges' in top_posts:
                            edges = top_posts['edges']
                            print(f"🏆 Top Posts edges count: {len(edges)}")
                            
                            # Look at first few top posts
                            for i, edge in enumerate(edges[:3]):
                                print(f"\n🏆 Top Post {i+1}:")
                                if isinstance(edge, dict) and 'node' in edge:
                                    node = edge['node']
                                    print(f"  Node keys: {list(node.keys())}")
                                    
                                    if 'accessibility_caption' in node:
                                        caption = node['accessibility_caption']
                                        print(f"  Caption: {caption[:100]}...")
                                        
                                        username = extract_username_from_caption(caption)
                                        if username:
                                            print(f"  ✅ Extracted username: @{username}")
                                        else:
                                            print(f"  ❌ No username found in caption")
            
            # Count total usernames we can extract
            usernames = extract_all_usernames(data)
            print(f"\n📊 SUMMARY:")
            print(f"  Total usernames extracted: {len(usernames)}")
            if usernames:
                print(f"  Sample usernames: {usernames[:5]}")
        
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def extract_username_from_caption(caption: str) -> Optional[str]:
    """Extract username from accessibility caption"""
    
    if not caption:
        return None
        
    patterns = [
        r'Photo shared by ([a-zA-Z0-9_.]+) on',
        r'Video shared by ([a-zA-Z0-9_.]+) on',
        r'Reel shared by ([a-zA-Z0-9_.]+) on',
        r'shared by ([a-zA-Z0-9_.]+) on',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            username = match.group(1)
            if re.match(r'^[a-zA-Z0-9_.]+$', username) and len(username) <= 30:
                return username
    
    return None

def extract_all_usernames(data: dict) -> list:
    """Extract all usernames from hashtag response"""
    
    usernames = []
    
    # Get posts from both regular and top posts
    posts_sources = []
    if 'posts' in data and isinstance(data['posts'], dict):
        posts_edges = data['posts'].get('edges', [])
        posts_sources.append(('posts', posts_edges))
        
    if 'top_posts' in data and isinstance(data['top_posts'], dict):
        top_posts_edges = data['top_posts'].get('edges', [])
        posts_sources.append(('top_posts', top_posts_edges))
    
    for source_type, edges in posts_sources:
        for edge in edges:
            if isinstance(edge, dict) and 'node' in edge:
                node = edge['node']
                if 'accessibility_caption' in node:
                    caption = node['accessibility_caption']
                    username = extract_username_from_caption(caption)
                    if username:
                        usernames.append(username)
    
    return list(set(usernames))  # Remove duplicates

def main():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    
    # Test multiple hashtags
    hashtags = ["luxury", "fashion", "style", "gaming"]
    
    for hashtag in hashtags:
        print(f"\n" + "="*80)
        debug_hashtag_search(hashtag, API_KEY)
        print("\n")

if __name__ == "__main__":
    main() 