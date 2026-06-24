#!/usr/bin/env python3
"""
Setup script for FP&A Agent System
"""

import os
import sys
from pathlib import Path
import json

# Create necessary directories
def create_directories():
    """Create necessary directories"""
    directories = [
        "./data",
        "./data/uploads",
        "./data/reports",
        "./data/chroma_db",
        "./src",
        "./src/agents",
        "./src/rag",
        "./src/workflows",
        "./src/analysis",
        "./src/utils",
        "./config"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create __init__.py files
    init_files = [
        "./src/agents/__init__.py",
        "./src/rag/__init__.py",
        "./src/workflows/__init__.py",
        "./src/analysis/__init__.py",
        "./src/utils/__init__.py",
        "./config/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✓ Created file: {init_file}")

def create_sample_files():
    """Create sample files"""
    # Create sample financial data
    sample_data = [
        {
            "department": "Marketing",
            "account_code": "5000",
            "account_name": "Advertising Expense",
            "period": "2024-01",
            "budget_amount": 50000.0,
            "actual_amount": 55000.0
        },
        {
            "department": "Marketing",
            "account_code": "5100",
            "account_name": "Travel Expense",
            "period": "2024-01",
            "budget_amount": 20000.0,
            "actual_amount": 15000.0
        },
        {
            "department": "Sales",
            "account_code": "5000",
            "account_name": "Advertising Expense",
            "period": "2024-01",
            "budget_amount": 30000.0,
            "actual_amount": 45000.0
        },
        {
            "department": "R&D",
            "account_code": "5200",
            "account_name": "Software License",
            "period": "2024-01",
            "budget_amount": 100000.0,
            "actual_amount": 120000.0
        },
        {
            "department": "Operations",
            "account_code": "5300",
            "account_name": "Consulting Fees",
            "period": "2024-01",
            "budget_amount": 75000.0,
            "actual_amount": 60000.0
        }
    ]
    
    with open("./data/sample_financial_data.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    print("✓ Created sample financial data")
    
    # Create sample invoice document
    sample_invoice = """INVOICE
Invoice Number: INV-2024-001
Date: 2024-01-15
Vendor: Digital Marketing Inc.
Department: Marketing
Account: Advertising Expense
Amount: $15,000.00
Description: Q1 Social Media Campaign
Approved by: John Smith
Approval Date: 2024-01-10"""
    
    with open("./data/uploads/sample_invoice.txt", "w") as f:
        f.write(sample_invoice)
    print("✓ Created sample invoice document")
    
    # Create sample contract
    sample_contract = """CONTRACT AGREEMENT
Contract ID: CONT-2024-001
Vendor: Tech Solutions LLC
Department: R&D
Account: Software License
Start Date: 2024-01-01
End Date: 2024-12-31
Total Value: $120,000.00
Monthly Payment: $10,000.00
Terms: Annual license for development software
Signed by: Jane Doe
Signature Date: 2023-12-15"""
    
    with open("./data/uploads/sample_contract.txt", "w") as f:
        f.write(sample_contract)
    print("✓ Created sample contract document")

def main():
    """Main setup function"""
    print("Setting up FP&A Agent System...")
    print("-" * 40)
    
    create_directories()
    print("-" * 40)
    create_sample_files()
    print("-" * 40)
    
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Ensure LM Studio is running at http://192.168.153.1:1234")
    print("2. Test installation: python test_installation.py")
    print("3. Run the system: python main.py --interactive")
    print("4. Or launch the web UI: streamlit run app.py")

if __name__ == "__main__":
    main()