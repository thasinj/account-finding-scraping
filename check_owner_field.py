#!/usr/bin/env python3
"""
Check the owner field structure in hashtag posts
"""

import requests
import json

def check_owner_field(hashtag: str, api_key: str):
    """Check what's in the owner field"""
    
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    clean_hashtag = hashtag.replace('#', '')
    url = f"{base_url}/search_hashtag.php?hashtag={clean_hashtag}"
    
    print(f"🔍 Checking owner field for #{hashtag}")
    print("=" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check posts
            if 'posts' in data and isinstance(data['posts'], dict):
                edges = data['posts'].get('edges', [])
                print(f"📮 Found {len(edges)} posts")
                
                # Look at first few posts' owner fields
                for i, edge in enumerate(edges[:5]):
                    print(f"\n🔍 Post {i+1}:")
                    
                    if isinstance(edge, dict) and 'node' in edge:
                        node = edge['node']
                        
                        if 'owner' in node:
                            owner = node['owner']
                            print(f"  👤 Owner type: {type(owner)}")
                            print(f"  👤 Owner content: {owner}")
                            
                            if isinstance(owner, dict):
                                print(f"  👤 Owner keys: {list(owner.keys())}")
                                if 'username' in owner:
                                    username = owner['username']
                                    print(f"  ✅ Username: {username}")
                                else:
                                    print(f"  ❌ No 'username' key in owner")
                            else:
                                print(f"  ⚠️  Owner is not a dict")
                        else:
                            print(f"  ❌ No 'owner' field in node")
                            print(f"  📋 Available keys: {list(node.keys())}")
            
            # Also check top posts
            if 'top_posts' in data and isinstance(data['top_posts'], dict):
                edges = data['top_posts'].get('edges', [])
                print(f"\n🏆 Found {len(edges)} top posts")
                
                # Look at first top post's owner field
                if edges:
                    edge = edges[0]
                    print(f"\n🏆 Top Post 1:")
                    
                    if isinstance(edge, dict) and 'node' in edge:
                        node = edge['node']
                        
                        if 'owner' in node:
                            owner = node['owner']
                            print(f"  👤 Owner: {owner}")
                            
                            if isinstance(owner, dict) and 'username' in owner:
                                username = owner['username']
                                print(f"  ✅ Username: {username}")
        
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    import os
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    
    # Check a few hashtags
    hashtags = ["luxury", "gaming"]
    
    for hashtag in hashtags:
        check_owner_field(hashtag, API_KEY)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main() 