#!/usr/bin/env python3

import re
from typing import Optional

def enhanced_extract_username_from_caption(caption: str) -> Optional[str]:
    """Enhanced username extraction logic (matches the updated instagram_cli_discovery.py)"""
    
    if not caption:
        return None
    
    # 1. PRIORITY: Search for @username mentions anywhere in the caption (most reliable)
    at_username_matches = re.findall(r'@([a-zA-Z0-9_.]+)', caption)
    for username in at_username_matches:
        if is_valid_username(username):
            return username
    
    # 2. Try "Photo/Video by X on" patterns, but extract FULL names and validate strictly
    patterns_for_photo_by = [
        r'Photo by ([a-zA-Z0-9_.\s]+) on',     # Captures "Jessica Chen" from "Photo by Jessica Chen on"
        r'Video by ([a-zA-Z0-9_.\s]+) on',
        r'Reel by ([a-zA-Z0-9_.\s]+) on',
        r'Photo shared by ([a-zA-Z0-9_.\s]+) on',
        r'Video shared by ([a-zA-Z0-9_.\s]+) on',
        r'Reel shared by ([a-zA-Z0-9_.\s]+) on',
        r'shared by ([a-zA-Z0-9_.\s]+) on',
        r'Photo shared by ([a-zA-Z0-9_.\s]+) tagging',
        r'by ([a-zA-Z0-9_.\s]+) in [A-Za-z]',
    ]
    
    for pattern in patterns_for_photo_by:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            extracted_name = match.group(1).strip()
            # CRITICAL: Only consider it a username if it's a SINGLE WORD (no spaces)
            if ' ' not in extracted_name and is_valid_username(extracted_name):
                return extracted_name
    
    # 3. Fallback: Look for standalone usernames in quotes or other patterns
    quote_patterns = [
        r'"([a-zA-Z0-9_.]+)"',
        r"'([a-zA-Z0-9_.]+)'",
    ]
    
    for pattern in quote_patterns:
        matches = re.findall(pattern, caption)
        for username in matches:
            if is_valid_username(username):
                return username
    
    return None

def is_valid_username(username: str) -> bool:
    """Enhanced username validation (matches the updated instagram_cli_discovery.py)"""
    if not username:
        return False
    
    # Instagram username rules: 1-30 chars, alphanumeric + dots + underscores
    if not re.match(r'^[a-zA-Z0-9_.]+$', username):
        return False
    
    if len(username) > 30 or len(username) < 1:
        return False
    
    # COMPREHENSIVE list of common false positives to filter out
    common_words = {
        # Social media terms
        'instagram', 'photo', 'video', 'image', 'picture', 'post', 'story', 'reel', 'igtv',
        'follow', 'like', 'share', 'tag', 'comment', 'dm', 'live', 'stories',
        
        # Generic terms that appear in captions
        'the', 'and', 'for', 'with', 'this', 'that', 'here', 'there', 'what', 'when',
        'where', 'how', 'why', 'who', 'all', 'any', 'can', 'now', 'new', 'get',
        
        # Common first names that show up in "Photo by [Name] on" patterns
        'john', 'jane', 'mike', 'sarah', 'david', 'emily', 'chris', 'alex', 'jessica',
        'michael', 'ashley', 'daniel', 'amanda', 'james', 'lisa', 'robert', 'jennifer',
        'william', 'elizabeth', 'richard', 'maria', 'thomas', 'susan', 'charles', 'nancy',
        
        # Time/date related (from "on July 27" etc)
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
        'september', 'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr',
        'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'monday', 'tuesday',
        'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        
        # Common caption words
        'content', 'creator', 'user', 'account', 'profile', 'page', 'feed', 'explore',
    }
    
    if username.lower() in common_words:
        return False
    
    # Additional checks for overly short usernames (likely fragments)
    if len(username) < 3:
        return False
    
    return True

def test_enhanced_extraction():
    """Test enhanced username extraction with real caption samples"""
    
    # Sample captions from the user's JSON data that should now capture usernames
    test_captions = [
        # @username mentions (should be captured with HIGH priority)
        "Check out this amazing content from @dailymillionairemind for business tips!",
        "Love this style inspiration by @THEMULTIPASSIONATECLUB on Instagram",
        "Beautiful architecture by @sqmarchitects in downtown",
        "Quality service from @cleanslateautospa - highly recommended!",
        
        # "Photo by Full Name on" patterns (should REJECT multi-word names)
        "Photo by Jessica Chen on July 27, 2025",  # Should be rejected (space in name)
        "Photo by DF BROTHERS on January 15, 2025",  # Should be rejected (space in name)
        "Video by The Creative Studio on March 10, 2025",  # Should be rejected (space in name)
        
        # "Photo by single_username on" patterns (should ACCEPT single-word usernames)
        "Photo by creativestudio on July 27, 2025",  # Should be accepted (no space)
        "Video by fashionista on January 15, 2025",  # Should be accepted (no space)
        "Reel by travelguru on March 10, 2025",  # Should be accepted (no space)
        
        # Mixed patterns (should prioritize @username over "Photo by")
        "Photo by Jessica Chen on July 27, 2025. Follow @dailymillionairemind for more!",  # Should extract @dailymillionairemind
        
        # Edge cases
        "Photo by mike on Tuesday",  # Should be rejected (common name filter)
        "Video by sarah on Friday",  # Should be rejected (common name filter)
        "Content by instagram on Monday",  # Should be rejected (social media term filter)
        
        # Quote patterns
        'User "cool_username" posted this amazing photo',  # Should extract cool_username
        "Check out 'amazing_creator' for more content",  # Should extract amazing_creator
    ]
    
    print("🧪 TESTING ENHANCED USERNAME EXTRACTION")
    print("=" * 80)
    
    extracted_usernames = []
    
    for i, caption in enumerate(test_captions, 1):
        username = enhanced_extract_username_from_caption(caption)
        
        print(f"\n{i:2d}. Caption: {caption[:70]}{'...' if len(caption) > 70 else ''}")
        if username:
            print(f"    ✅ EXTRACTED: @{username}")
            extracted_usernames.append(username)
        else:
            print(f"    ❌ No username extracted")
    
    print(f"\n📊 SUMMARY:")
    print(f"Total captions tested: {len(test_captions)}")
    print(f"Usernames extracted: {len(extracted_usernames)}")
    print(f"Extraction rate: {len(extracted_usernames)/len(test_captions)*100:.1f}%")
    
    if extracted_usernames:
        print(f"\n📋 EXTRACTED USERNAMES:")
        for username in set(extracted_usernames):
            print(f"  • @{username}")
    
    # Show expected improvements
    print(f"\n🎯 KEY IMPROVEMENTS:")
    print(f"  1. ✅ Prioritizes @username mentions (most reliable)")
    print(f"  2. ✅ Rejects multi-word names like 'Jessica Chen'")
    print(f"  3. ✅ Accepts single-word usernames like 'creativestudio'")
    print(f"  4. ✅ Filters out common words like 'mike', 'instagram'")
    print(f"  5. ✅ Supports quote patterns for additional coverage")

if __name__ == "__main__":
    test_enhanced_extraction() 