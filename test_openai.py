#!/usr/bin/env python3
"""
OpenAI API Connection Test Script
Tests the OpenAI API connection and environment variables
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Variables...")
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("   Make sure you have a .env file with OPENAI_API_KEY=your_key_here")
        return False
    
    if api_key.startswith('sk-'):
        print("✅ OPENAI_API_KEY found and has correct format")
        print(f"   Key starts with: {api_key[:12]}...")
    else:
        print("⚠️  OPENAI_API_KEY found but may have incorrect format")
        print("   OpenAI API keys should start with 'sk-'")
        print(f"   Your key starts with: {api_key[:12]}...")
    
    return True

def test_openai_import():
    """Test OpenAI library import"""
    print("\n📦 Testing OpenAI Library Import...")
    
    try:
        from openai import OpenAI
        print("✅ OpenAI library imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import OpenAI library: {e}")
        print("   Run: pip install openai")
        return False

def test_openai_client():
    """Test OpenAI client initialization"""
    print("\n🔗 Testing OpenAI Client Initialization...")
    
    try:
        from openai import OpenAI
        
        # Try the same initialization as in app.py
        try:
            client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            print("✅ OpenAI client initialized successfully")
            return client
        except TypeError as e:
            if 'proxies' in str(e):
                print("⚠️  Proxy configuration issue detected, using workaround...")
                import httpx
                client = OpenAI(
                    api_key=os.getenv('OPENAI_API_KEY'),
                    http_client=httpx.Client()
                )
                print("✅ OpenAI client initialized with proxy workaround")
                return client
            else:
                raise e
                
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return None

def test_api_connection(client):
    """Test actual API connection"""
    print("\n🌐 Testing OpenAI API Connection...")
    
    if not client:
        print("❌ Cannot test API - client not initialized")
        return False
    
    try:
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond with exactly 'API test successful' and nothing else."},
                {"role": "user", "content": "Test message"}
            ],
            max_tokens=10,
            temperature=0
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"✅ API connection successful!")
        print(f"   Model: {response.model}")
        print(f"   Response: {response_text}")
        
        # Check token usage
        if hasattr(response, 'usage'):
            print(f"   Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if 'invalid api key' in error_str or 'unauthorized' in error_str:
            print("   🔑 This looks like an API key issue")
            print("   - Check that your API key is correct in .env file")
            print("   - Make sure your OpenAI API key is active")
            print("   - Verify you have sufficient credits")
        elif 'rate limit' in error_str:
            print("   ⏰ Rate limit exceeded - wait a moment and try again")
        elif 'network' in error_str or 'connection' in error_str:
            print("   🌐 Network connection issue")
            print("   - Check your internet connection")
            print("   - Try again in a moment")
        
        return False

def main():
    """Run all tests"""
    print("🚀 OpenAI API Connection Test\n")
    
    # Test environment
    if not test_environment():
        sys.exit(1)
    
    # Test import
    if not test_openai_import():
        sys.exit(1)
    
    # Test client initialization
    client = test_openai_client()
    if not client:
        sys.exit(1)
    
    # Test API connection
    if not test_api_connection(client):
        sys.exit(1)
    
    print("\n🎉 All tests passed! OpenAI API is ready to use.")
    print("\nYou can now run the Agora Chat application with confidence.")

if __name__ == "__main__":
    main()