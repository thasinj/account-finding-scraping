#!/usr/bin/env python3
"""
Debug why CLI extraction is getting fewer usernames than the working version
"""

import requests
import json
import re
from typing import Optional, List

def test_cli_extraction(hashtag: str, api_key: str):
    """Test the CLI extraction method"""
    
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    clean_hashtag = hashtag.replace('#', '')
    url = f"{base_url}/search_hashtag.php?hashtag={clean_hashtag}"
    
    print(f"🔍 Testing CLI extraction for #{hashtag}")
    print("=" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # CLI method (current)
            cli_usernames = cli_extract_usernames_from_posts(data)
            print(f"🔧 CLI method: {len(cli_usernames)} usernames")
            if cli_usernames:
                print(f"   Sample: {cli_usernames[:5]}")
            
            # Working method (from fix script)
            working_usernames = working_extract_usernames_from_posts(data)
            print(f"✅ Working method: {len(working_usernames)} usernames")
            if working_usernames:
                print(f"   Sample: {working_usernames[:5]}")
            
            # Compare
            missing = set(working_usernames) - set(cli_usernames)
            if missing:
                print(f"❌ CLI is missing {len(missing)} usernames: {list(missing)[:5]}")
            
            return cli_usernames, working_usernames
        
        else:
            print(f"❌ API Error: {response.status_code}")
            return [], []
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return [], []

def cli_extract_usernames_from_posts(data: dict) -> List[str]:
    """CLI extraction method (current)"""
    
    usernames = []
    
    # Get posts from both regular and top posts
    posts_sources = []
    if 'posts' in data and isinstance(data['posts'], dict):
        posts_edges = data['posts'].get('edges', [])
        posts_sources.append(posts_edges)
        
    if 'top_posts' in data and isinstance(data['top_posts'], dict):
        top_posts_edges = data['top_posts'].get('edges', [])
        posts_sources.append(top_posts_edges)
    
    for edges in posts_sources:
        for edge in edges:
            if isinstance(edge, dict) and 'node' in edge:
                node = edge['node']
                
                if 'accessibility_caption' in node:
                    caption = node['accessibility_caption']
                    username = cli_extract_username_from_caption(caption)
                    if username:
                        usernames.append(username)
    
    return list(set(usernames))

def cli_extract_username_from_caption(caption: str) -> Optional[str]:
    """CLI caption extraction (current)"""
    
    if not caption:
        return None
        
    patterns = [
        r'Photo by ([a-zA-Z0-9_.]+) on',
        r'Video by ([a-zA-Z0-9_.]+) on',
        r'Reel by ([a-zA-Z0-9_.]+) on',
        r'Photo shared by ([a-zA-Z0-9_.]+) on',
        r'Video shared by ([a-zA-Z0-9_.]+) on',
        r'shared by ([a-zA-Z0-9_.]+) on',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            username = match.group(1)
            if cli_is_valid_username(username):
                return username
    
    return None

def cli_is_valid_username(username: str) -> bool:
    """CLI username validation (current)"""
    if not username or len(username) > 30:
        return False
    
    if not re.match(r'^[a-zA-Z0-9_.]+$', username):
        return False
    
    common_words = {'instagram', 'photo', 'video', 'image'}
    if username.lower() in common_words:
        return False
    
    return True

def working_extract_usernames_from_posts(data: dict) -> List[str]:
    """Working extraction method (from fix script)"""
    
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
                    username = working_extract_username_from_caption(caption)
                    if username:
                        usernames.append(username)
    
    return list(set(usernames))

def working_extract_username_from_caption(caption: str) -> Optional[str]:
    """Working caption extraction (from fix script)"""
    
    if not caption:
        return None
    
    # Updated patterns for current format
    patterns = [
        # New format: "Photo by username on"
        r'Photo by ([a-zA-Z0-9_.]+) on',
        r'Video by ([a-zA-Z0-9_.]+) on',
        r'Reel by ([a-zA-Z0-9_.]+) on',
        
        # Old format (backup)
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
            if working_is_valid_username(username):
                return username
    
    return None

def working_is_valid_username(username: str) -> bool:
    """Working username validation (from fix script)"""
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
    
    # Test the same hashtags
    hashtags = ["business", "fashion", "gaming"]
    
    for hashtag in hashtags:
        print(f"\n" + "="*80)
        cli_usernames, working_usernames = test_cli_extraction(hashtag, API_KEY)
        
        print(f"\n📊 COMPARISON for #{hashtag}:")
        print(f"   CLI: {len(cli_usernames)} usernames")
        print(f"   Working: {len(working_usernames)} usernames")
        print(f"   Difference: {len(working_usernames) - len(cli_usernames)}")
        
        if len(working_usernames) > len(cli_usernames):
            print(f"   🐛 CLI method is missing usernames!")

if __name__ == "__main__":
    main() 