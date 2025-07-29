#!/usr/bin/env python3
"""
Debug script to understand what's being parsed from the avatar config
"""

import re

def debug_avatar_config():
    """Debug the avatar configuration parsing"""
    try:
        with open('avatar_config.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📄 Full file content:")
        print(content)
        print("\n" + "="*50)
        
        # Split content by avatar sections (### headers)
        sections = re.split(r'\n### ', content)
        
        print(f"\n📋 Found {len(sections)} sections total:")
        for i, section in enumerate(sections):
            print(f"\nSection {i}:")
            print(f"First 100 chars: {repr(section[:100])}")
            if i > 0:  # Skip the first section (title)
                lines = section.strip().split('\n')
                if lines:
                    avatar_key = lines[0].lower().strip()
                    print(f"Avatar key would be: '{avatar_key}'")
                    
                    # Check if we should stop parsing
                    if avatar_key in ['configuration notes', 'examples'] or avatar_key.startswith('#'):
                        print(f"Would stop parsing at: {avatar_key}")
                        break
        
    except FileNotFoundError:
        print("❌ avatar_config.md not found")

if __name__ == "__main__":
    debug_avatar_config()