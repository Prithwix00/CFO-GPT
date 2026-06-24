# check_versions.py
import importlib.metadata as metadata

packages = [
    "langchain",
    "langchain-core", 
    "langchain-community",
    "langgraph",
    "chromadb",
    "streamlit",
    "pydantic",
    "pydantic-settings",
    "streamlit-option-menu"
]

print("Checking installed versions...")
print("=" * 50)

for package in packages:
    try:
        version = metadata.version(package)
        print(f"✅ {package:25} {version}")
    except:
        print(f"❌ {package:25} NOT INSTALLED")

print("=" * 50)
print("\nExpected versions:")
print("- langchain: 0.1.16")
print("- langchain-core: 0.1.45")
print("- streamlit: 1.36.0+")
print("- pydantic: 2.6.4+")