#!/usr/bin/env python3
"""
Test script for LM Studio connection using requests
"""

import sys
import requests
import json

def test_lm_studio():
    """Test LM Studio connection using simple HTTP requests"""
    print("Testing LM Studio connection...")
    print(f"URL: http://192.168.153.1:1234")
    
    try:
        # Test 1: Check if LM Studio is running
        print("\n1. Checking if LM Studio server is running...")
        response = requests.get("http://192.168.153.1:1234/v1/models", timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ LM Studio is running!")
            print(f"   Available models: {models.get('data', [])}")
        else:
            print(f"❌ LM Studio returned status: {response.status_code}")
            return False
        
        # Test 2: Try a simple chat completion
        print("\n2. Testing chat completion...")
        payload = {
            "model": "deepseek-r1-distill-qwen-7b",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, please respond with 'OK' if you can hear me."}
            ],
            "temperature": 0.1,
            "max_tokens": 100
        }
        
        response = requests.post(
            "http://192.168.153.1:1234/v1/chat/completions",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            print(f"✅ Chat completion successful!")
            print(f"   Response: {reply[:100]}...")
            return True
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to LM Studio at http://192.168.153.1:1234")
        print("\nTroubleshooting tips:")
        print("1. Ensure LM Studio is running")
        print("2. Check if the IP address is correct")
        print("3. Verify the port (default is 1234)")
        print("4. Check firewall/network settings")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_lm_studio()
    sys.exit(0 if success else 1)