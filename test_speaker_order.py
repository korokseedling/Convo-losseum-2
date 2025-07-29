#!/usr/bin/env python3
"""
Test script for speaker order functionality
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the app module
sys.path.append('.')
from app import load_avatar_config, get_ai_order

def test_speaker_order():
    """Test the speaker order functionality"""
    print("🎭 Testing Speaker Order Functionality\n")
    
    # Load avatar configuration
    avatars = load_avatar_config()
    
    print("📋 Loaded Avatar Configuration:")
    for key, config in avatars.items():
        active_status = "✅ Active" if config.get('active', True) else "❌ Inactive"
        speaker_order = config.get('speaker_order', 999)
        name = config.get('name', key.title())
        print(f"  {name} ({key}): {active_status}, Speaker Order: {speaker_order}")
    
    print("\n🗣️  AI Speaking Order:")
    ai_order = get_ai_order()
    
    if ai_order:
        for i, character_key in enumerate(ai_order, 1):
            character_config = avatars.get(character_key, {})
            name = character_config.get('name', character_key.title())
            speaker_order = character_config.get('speaker_order', 999)
            print(f"  {i}. {name} (order: {speaker_order})")
    else:
        print("  No active avatars found!")
    
    print(f"\n📊 Total active avatars: {len(ai_order)}")
    
    # Test edge cases
    print("\n🧪 Testing Edge Cases:")
    
    # Check if order is consistent
    order1 = get_ai_order()
    order2 = get_ai_order() 
    if order1 == order2:
        print("  ✅ Order is consistent across calls")
    else:
        print("  ❌ Order is inconsistent!")
    
    # Check if only active avatars are included
    active_count = sum(1 for config in avatars.values() if config.get('active', True))
    if len(ai_order) == active_count:
        print("  ✅ Only active avatars included in order")
    else:
        print(f"  ❌ Mismatch: {len(ai_order)} in order vs {active_count} active")

if __name__ == "__main__":
    test_speaker_order()