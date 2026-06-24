# test_lm_connection.py
import requests
import json
import sys

def test_lm_studio():
    print("=" * 60)
    print("Testing LM Studio Connection")
    print("=" * 60)
    
    base_url = "http://192.168.153.1:1234"
    model = "deepseek-r1-distill-qwen-7b"
    
    try:
        # Test 1: Check if server is running
        print("\n1. Checking if LM Studio is running...")
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ LM Studio is running!")
            if 'data' in models and models['data']:
                print(f"   Available models: {[m['id'] for m in models['data']]}")
            else:
                print(f"   Response: {models}")
        else:
            print(f"❌ LM Studio returned status: {response.status_code}")
            return False
        
        # Test 2: Simple chat completion
        print("\n2. Testing chat completion with model...")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, please respond with 'OK' if you can hear me."}
            ],
            "temperature": 0.1,
            "max_tokens": 100,
            "stream": False
        }
        
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            print(f"✅ Chat completion successful!")
            print(f"   Response: {reply}")
            return True
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to LM Studio at {base_url}")
        print("\nTroubleshooting:")
        print("1. Ensure LM Studio is running")
        print("2. Check the IP address (should be the machine running LM Studio)")
        print("3. Default port is 1234")
        print("4. In LM Studio: Go to 'Local Server' tab and ensure server is running")
        return False
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_lm_studio()
    print("\n" + "=" * 60)
    if success:
        print("✅ LM Studio is ready!")
        sys.exit(0)
    else:
        print("❌ LM Studio connection failed")
        sys.exit(1)