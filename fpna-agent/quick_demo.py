# quick_demo.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🚀 FP&A Agent Quick Demo")
print("=" * 60)

# 1. Generate sample data
from src.utils.data_loader import DataLoader
loader = DataLoader()
data = loader.generate_sample_data()
print(f"📊 Generated {len(data)} financial records")

# 2. Detect variances
from src.agents.monitor_agent import MonitorAgent
monitor = MonitorAgent()
results = monitor.detect_variances(data)

sig_vars = results["significant_variances"]
print(f"🔍 Found {len(sig_vars)} significant variances")

# 3. Show top variances
if sig_vars:
    print("\n📈 Top 3 Significant Variances:")
    for i, var in enumerate(sig_vars[:3], 1):
        print(f"   {i}. {var['department']} - {var['account_name']}")
        print(f"      Budget: ${var['budget']:,.2f}, Actual: ${var['actual']:,.2f}")
        print(f"      Variance: ${var['variance_amount']:,.2f} ({var['variance_percentage']:.1f}%)")
        print(f"      Reason: {var['reason']}")
        print()

# 4. Try RAG if documents exist
import os
if os.path.exists("./data/uploads") and os.listdir("./data/uploads"):
    print("📄 Testing RAG with uploaded documents...")
    from src.rag.loader import DocumentLoader
    from src.rag.vector_store import VectorStore
    from src.rag.retriever import RAGRetriever
    
    doc_loader = DocumentLoader()
    documents = doc_loader.load_directory("./data/uploads")
    
    if documents:
        vector_store = VectorStore()
        vector_store.add_documents(documents)
        
        rag = RAGRetriever(vector_store, monitor)
        
        # Test search
        result = rag.retrieve_relevant_documents("invoice marketing")
        print(f"   Found {result['total_found']} relevant documents")
    else:
        print("   No documents found in uploads directory")
else:
    print("📄 No documents uploaded yet (optional)")

print("\n" + "=" * 60)
print("✅ Demo complete! System is working.")
print("\nFor full features:")
print("1. Upload documents to ./data/uploads/")
print("2. Run: python main.py --interactive")
print("3. OR: streamlit run app.py")