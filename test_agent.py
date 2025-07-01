#!/usr/bin/env python3
"""
Test script for Jarvis AI Agent
Run this to test the agent functionality locally
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your deployed URL
TEST_USER_ID = "test_user_123"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
            print(f"   Model: {data['model']}")
            print(f"   Storage: {data['storage']}")
            print(f"   AI Ready: {data['ai_ready']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_talk_endpoint():
    """Test the main talk endpoint"""
    print("\n💬 Testing talk endpoint...")
    
    test_messages = [
        "Hello! How are you today?",
        "What's the weather like?",
        "Can you help me with a coding problem?",
        "Tell me a joke"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Message {i}: {message}")
        try:
            response = requests.post(f"{BASE_URL}/talk", json={
                "text": message,
                "user_id": TEST_USER_ID
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Reply: {data['reply'][:100]}...")
                print(f"   📝 Message ID: {data['message_id']}")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")
        
        time.sleep(1)  # Small delay between requests

def test_history_endpoint():
    """Test the history endpoint"""
    print("\n📚 Testing history endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/history/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ History retrieved successfully")
            print(f"   User ID: {data['user_id']}")
            print(f"   Message count: {data['count']}")
            
            # Show last few messages
            if data['messages']:
                print("   Recent messages:")
                for msg in data['messages'][-3:]:  # Last 3 messages
                    role = msg['role']
                    content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                    print(f"     {role}: {content}")
        else:
            print(f"❌ History error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ History request error: {e}")

def test_clear_history():
    """Test clearing history"""
    print("\n🗑️ Testing clear history...")
    try:
        response = requests.delete(f"{BASE_URL}/history/{TEST_USER_ID}")
        
        if response.status_code == 200:
            print("✅ History cleared successfully")
        else:
            print(f"❌ Clear history error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Clear history request error: {e}")

def test_error_handling():
    """Test error handling"""
    print("\n⚠️ Testing error handling...")
    
    # Test with invalid JSON
    try:
        response = requests.post(f"{BASE_URL}/talk", 
                               data="invalid json",
                               headers={"Content-Type": "application/json"})
        print(f"   Invalid JSON test: {response.status_code}")
    except Exception as e:
        print(f"   Invalid JSON error: {e}")
    
    # Test with missing fields
    try:
        response = requests.post(f"{BASE_URL}/talk", json={"text": "test"})
        print(f"   Missing user_id test: {response.status_code}")
    except Exception as e:
        print(f"   Missing user_id error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Jarvis AI Agent Tests")
    print("=" * 50)
    
    # Check if server is running
    if not test_health_check():
        print("\n❌ Server is not running. Please start the server first:")
        print("   python main.py")
        return
    
    # Run tests
    test_talk_endpoint()
    test_history_endpoint()
    test_clear_history()
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\nTo test with your deployed agent, change BASE_URL in this script.")

if __name__ == "__main__":
    main() 