#!/usr/bin/env python3
"""
Test if all dependencies are installed correctly for LM Studio version
"""

import importlib
import sys

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            module = importlib.import_module(module_name, package=package_name)
        else:
            module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError as e:
        return False, str(e)

def main():
    print("Testing FP&A Agent Dependencies (LM Studio Version)...")
    print("=" * 60)
    
    tests = [
        # Core LangChain (NO OpenAI packages needed)
        ("langchain", None),
        ("langchain_core", None),
        ("langchain_community", None),
        ("langgraph", None),
        
        # Vector DB
        ("chromadb", None),
        
        # IMPORTANT: These should NOT be installed
        # ("langchain_openai", None),  # Should NOT be installed
        # ("openai", None),  # Should NOT be installed
        
        # UI
        ("streamlit", None),
        
        # Data
        ("pandas", None),
        ("numpy", None),
        
        # Documents
        ("pypdf", None),
        ("docx", None),
        ("pdfplumber", None),
        
        # Config
        ("pydantic", None),
        ("dotenv", None),
        
        # HTTP Client (for LM Studio)
        ("requests", None),
        ("aiohttp", None),
        
        # Embeddings are provided by LM Studio's OpenAI-compatible API.
    ]
    
    all_passed = True
    
    for module_name, package_name in tests:
        success, info = test_import(module_name, package_name)
        
        if success:
            print(f"✅ {module_name}: {info}")
        else:
            print(f"❌ {module_name}: {info}")
            all_passed = False
    
    print("=" * 60)
    
    # Test LM Studio connection with requests
    print("\nTesting LM Studio connection with requests...")
    try:
        import requests
        response = requests.get("http://192.168.153.1:1234/v1/models", timeout=5)
        if response.status_code == 200:
            print("✅ LM Studio is reachable")
            print(f"   Response: {response.json()}")
        else:
            print(f"⚠️  LM Studio returned status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cannot connect to LM Studio: {e}")
    
    if all_passed:
        print("\n🎉 All dependencies are installed correctly for LM Studio version!")
    else:
        print("\n⚠️  Some dependencies are missing.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
