# test_reporter.py
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🧪 Testing Reporter Agent")
print("="*60)

from src.agents.reporter_agent import ReporterAgent
import json

# Create reporter agent
reporter = ReporterAgent()

print(f"📁 Reports directory: {reporter.reports_dir}")
print(f"Directory exists: {reporter.reports_dir.exists()}")
print(f"Files in directory: {len(list(reporter.reports_dir.glob('*')))}")

# Test 1: Generate budget proposal
print("\n1️⃣ Testing budget proposal generation...")
test_variance = {
    "department": "Marketing",
    "account_name": "Advertising Expense",
    "account_code": "5001",
    "period": "Q1 2024",
    "budget": 50000.00,
    "actual": 55000.00,
    "variance_amount": 5000.00,
    "variance_percentage": 10.0
}

test_investigation = {
    "analysis": "Overspend due to successful campaign performance",
    "confidence": 85.0,
    "evidence_count": 2
}

proposal = reporter.generate_budget_adjustment_proposal(
    test_variance, 
    test_investigation, 
    "Marketing"
)

print(f"   Status: {proposal.get('status')}")
print(f"   Department: {proposal.get('department')}")
print(f"   Account: {proposal.get('account')}")
print(f"   Adjustment Amount: ${proposal.get('adjustment_amount', 0):,.2f}")
print(f"   Adjustment Type: {proposal.get('adjustment_type')}")
print(f"   Justification: {proposal.get('justification', '')[:80]}...")

# Test 2: Check if file was created
print("\n2️⃣ Checking for created files...")
files = list(reporter.reports_dir.glob("*"))
if files:
    print(f"   Found {len(files)} files:")
    for f in files[:5]:
        print(f"     - {f.name} ({f.stat().st_size:,} bytes)")
        
        # Show content of JSON files
        if f.suffix == '.json':
            try:
                with open(f, 'r') as json_file:
                    data = json.load(json_file)
                    print(f"       Status: {data.get('status')}")
                    print(f"       Type: {data.get('adjustment_type')}")
                    print(f"       Amount: ${data.get('adjustment_amount', 0):,.2f}")
            except:
                pass
else:
    print("   No files found in reports directory")

# Test 3: Generate executive summary
print("\n3️⃣ Testing executive summary generation...")
test_results = [
    {
        "department": "Marketing",
        "evidence_found": 2,
        "variance_details": {
            "account_name": "Advertising Expense",
            "variance_amount": 5000.00,
            "variance_percentage": 10.0
        },
        "investigation_result": {
            "confidence": 85.0,
            "analysis": "Campaign overspend"
        }
    },
    {
        "department": "Sales",
        "evidence_found": 3,
        "variance_details": {
            "account_name": "Software License",
            "variance_amount": 15000.00,
            "variance_percentage": 30.0
        },
        "investigation_result": {
            "confidence": 90.0,
            "analysis": "New software purchase"
        }
    }
]

summary = reporter.generate_executive_summary(test_results)
print(f"   Status: {summary.get('status')}")
print(f"   Filepath: {summary.get('filepath', 'No filepath')}")
print(f"   Summary preview: {summary.get('summary', '')[:100]}...")

# Test 4: Check directory again
print("\n4️⃣ Final directory check...")
files = list(reporter.reports_dir.glob("*"))
print(f"   Total files: {len(files)}")
if files:
    print("   Recent files:")
    for f in files[-3:]:
        print(f"     - {f.name}")

print("\n" + "="*60)
print("✅ Reporter Agent Test Complete")
print("\nNext steps:")
print("1. Run: python main.py --interactive")
print("2. Choose option 1 for complete analysis")
print("3. Check if reports are generated in: data/reports/")