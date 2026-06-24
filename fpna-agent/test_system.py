# test_system.py
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing FP&A Agent System Components...")
print("=" * 60)

# Test 1: Configuration
print("\n1. Testing configuration...")
try:
    from config.settings import settings
    print(f"✅ Configuration loaded")
    print(f"   LM Studio URL: {settings.LMSTUDIO_BASE_URL}")
    print(f"   Model: {settings.MODEL_ID}")
    print(f"   Data dir: {settings.DATA_DIR}")
except Exception as e:
    print(f"❌ Configuration failed: {e}")

# Test 2: Data Loader
print("\n2. Testing data loader...")
try:
    from src.utils.data_loader import DataLoader, FinancialData
    loader = DataLoader()
    sample_data = loader.generate_sample_data()
    print(f"✅ Data loader working")
    print(f"   Generated {len(sample_data)} sample records")
except Exception as e:
    print(f"❌ Data loader failed: {e}")

# Test 3: Document Loader
print("\n3. Testing document loader...")
try:
    from src.rag.loader import DocumentLoader
    doc_loader = DocumentLoader()
    print(f"✅ Document loader imported")
except Exception as e:
    print(f"❌ Document loader failed: {e}")

# Test 4: Vector Store
print("\n4. Testing vector store...")
try:
    from src.rag.vector_store import VectorStore
    vector_store = VectorStore()
    print(f"✅ Vector store initialized")
except Exception as e:
    print(f"❌ Vector store failed: {e}")

# Test 5: Monitor Agent
print("\n5. Testing monitor agent...")
try:
    from src.agents.monitor_agent import MonitorAgent
    monitor = MonitorAgent()
    print(f"✅ Monitor agent initialized")
except Exception as e:
    print(f"❌ Monitor agent failed: {e}")

print("\n" + "=" * 60)
print("System component test complete!")
print("\nNext: Run the actual system with:")
print("  python main.py --interactive")
print("  OR")
print("  streamlit run app.py")