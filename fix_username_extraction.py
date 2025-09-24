#!/usr/bin/env python3
"""
Fixed username extraction from hashtag posts
"""

import requests
import json
import re
from typing import Optional, List

def test_fixed_extraction(hashtag: str, api_key: str):
    """Test the fixed username extraction"""
    
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    clean_hashtag = hashtag.replace('#', '')
    url = f"{base_url}/search_hashtag.php?hashtag={clean_hashtag}"
    
    print(f"🔧 Testing FIXED extraction for #{hashtag}")
    print("=" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Method 1: Extract from owner field (most reliable)
            usernames_from_owner = extract_usernames_from_owner(data)
            print(f"👤 Usernames from owner field: {len(usernames_from_owner)}")
            if usernames_from_owner:
                print(f"   Sample: {usernames_from_owner[:5]}")
            
            # Method 2: Extract from updated caption patterns
            usernames_from_caption = extract_usernames_from_fixed_captions(data)
            print(f"💬 Usernames from captions: {len(usernames_from_caption)}")
            if usernames_from_caption:
                print(f"   Sample: {usernames_from_caption[:5]}")
            
            # Combined results
            all_usernames = list(set(usernames_from_owner + usernames_from_caption))
            print(f"✅ Total unique usernames: {len(all_usernames)}")
            if all_usernames:
                print(f"   Combined sample: {all_usernames[:10]}")
            
            return all_usernames
        
        else:
            print(f"❌ API Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

def extract_usernames_from_owner(data: dict) -> List[str]:
    """Extract usernames from owner field (most reliable method)"""
    
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
                
                # Extract from owner field
                if 'owner' in node and isinstance(node['owner'], dict):
                    owner = node['owner']
                    if 'username' in owner:
                        username = owner['username']
                        if username and is_valid_username(username):
                            usernames.append(username)
    
    return list(set(usernames))  # Remove duplicates

def extract_usernames_from_fixed_captions(data: dict) -> List[str]:
    """Extract usernames from accessibility captions with updated patterns"""
    
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
                    username = extract_username_from_new_caption_format(caption)
                    if username:
                        usernames.append(username)
    
    return list(set(usernames))  # Remove duplicates

def extract_username_from_new_caption_format(caption: str) -> Optional[str]:
    """Extract username from NEW accessibility caption format"""
    
    if not caption:
        return None
    
    # Updated patterns for current format
    patterns = [
        # New format: "Photo by username on"
        r'Photo by ([a-zA-Z0-9_.]+) on',
        r'Video by ([a-zA-Z0-9_.]+) on',
        r'Reel by ([a-zA-Z0-9_.]+) on',
        
        # Old format (still try these as backup)
        r'Photo shared by ([a-zA-Z0-9_.]+) on',
        r'Video shared by ([a-zA-Z0-9_.]+) on',
        r'Reel shared by ([a-zA-Z0-9_.]+) on',
        r'shared by ([a-zA-Z0-9_.]+) on',
        
        # Additional patterns found in debug
        r'Photo shared by ([a-zA-Z0-9_.]+) tagging',
        r'by ([a-zA-Z0-9_.]+) in [A-Za-z]',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            username = match.group(1)
            if is_valid_username(username):
                return username
    
    return None

def is_valid_username(username: str) -> bool:
    """Check if username is valid Instagram format"""
    if not username:
        return False
    
    # Instagram username rules: 1-30 chars, alphanumeric + dots + underscores
    if not re.match(r'^[a-zA-Z0-9_.]+$', username):
        return False
    
    if len(username) > 30 or len(username) < 1:
        return False
    
    # Avoid common false positives
    common_words = {'instagram', 'photo', 'video', 'image', 'picture', 'post', 'story'}
    if username.lower() in common_words:
        return False
    
    return True

def main():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    
    # Test the fix on multiple hashtags
    hashtags = ["luxury", "fashion", "style", "gaming"]
    
    all_results = {}
    
    for hashtag in hashtags:
        print(f"\n" + "="*80)
        usernames = test_fixed_extraction(hashtag, API_KEY)
        all_results[hashtag] = usernames
        print("\n")
    
    # Summary
    print("="*80)
    print("🎯 FIXED EXTRACTION SUMMARY:")
    print("="*80)
    
    total_usernames = 0
    for hashtag, usernames in all_results.items():
        total_usernames += len(usernames)
        print(f"#{hashtag}: {len(usernames)} usernames")
    
    print(f"\nTotal usernames extracted: {total_usernames}")
    
    if total_usernames > 0:
        print(f"✅ USERNAME EXTRACTION FIXED!")
        print(f"🚀 Ready to update the discovery system!")
    else:
        print(f"❌ Still having issues - need more investigation")

if __name__ == "__main__":
    main() 