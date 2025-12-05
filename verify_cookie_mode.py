"""
Quick verification script for WebAI-to-API cookie mode
"""
import requests
import json

print("\n" + "="*70)
print("  WebAI-to-API Cookie Mode Verification")
print("="*70)

base_url = "http://localhost:6969"

# Test 1: Health check
print("\n[1/3] Testing health endpoint...")
try:
    response = requests.get(f"{base_url}/health", timeout=5)
    if response.status_code == 200:
        print("  ✅ Server is running")
    else:
        print(f"  ❌ Server returned {response.status_code}")
except Exception as e:
    print(f"  ❌ Server not reachable: {e}")
    print("\n  Make sure WebAI-to-API is running: python src\\run.py")
    exit(1)

# Test 2: Models endpoint
print("\n[2/3] Testing models endpoint...")
try:
    response = requests.get(f"{base_url}/v1/models", timeout=5)
    if response.status_code == 200:
        models = response.json()
        print(f"  ✅ Models endpoint working")
        if 'data' in models:
            print(f"  📋 Available models: {len(models['data'])}")
            for model in models['data'][:3]:
                print(f"     - {model.get('id', 'unknown')}")
    else:
        print(f"  ⚠️  Models endpoint returned {response.status_code}")
except Exception as e:
    print(f"  ❌ Models endpoint failed: {e}")

# Test 3: Chat completion (actual Gemini test)
print("\n[3/3] Testing chat completion with Gemini...")
try:
    payload = {
        "model": "gemini-3.0-pro",
        "messages": [
            {"role": "user", "content": "Say 'Cookie mode working!' if you can read this"}
        ],
        "max_tokens": 50
    }
    
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            message = data['choices'][0]['message']['content']
            print(f"  ✅ Chat completion successful!")
            print(f"  💬 Gemini response: {message[:100]}")
            
            # Check usage
            if 'usage' in data:
                print(f"  📊 Tokens used: {data['usage']}")
        else:
            print(f"  ⚠️  Unexpected response format: {data}")
    else:
        print(f"  ❌ Chat completion failed with status {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
except Exception as e:
    print(f"  ❌ Chat completion error: {e}")

print("\n" + "="*70)
print("  Verification Complete")
print("="*70)

print("\n💡 Next steps:")
print("  1. If all tests passed ✅ → Cookie mode is working!")
print("  2. Configure app4/.env with:")
print("     USE_LOCAL_GEMINI=true")
print("     WEBAI_API_BASE_URL=http://localhost:6969/v1")
print("  3. Test app4: cd app4 && python test_simple.py")
print()
