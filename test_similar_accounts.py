#!/usr/bin/env python3
"""
Test the similar accounts endpoint to debug response format
"""

import requests
import json
import os

def test_similar_accounts_endpoint():
    API_KEY = os.getenv("INSTAGRAM_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set INSTAGRAM_API_KEY env var")
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    }
    
    # Test with a well-known account
    test_usernames = ["insightsgta", "style", "luxury", "nike"]
    
    for username in test_usernames:
        print(f"\n🔍 Testing similar accounts for @{username}")
        print("=" * 60)
        
        url = f"{base_url}/get_ig_similar_accounts.php?username_or_url={username}"
        print(f"📡 URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=20)
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Got JSON response")
                    print(f"📄 Response type: {type(data)}")
                    
                    # Save response for analysis
                    filename = f"similar_accounts_debug_{username}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"💾 Response saved to {filename}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"📄 Raw response: {response.text[:200]}...")
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")

if __name__ == "__main__":
    test_similar_accounts_endpoint() 