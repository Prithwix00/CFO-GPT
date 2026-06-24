import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional
import os
from datetime import datetime
from pydantic import BaseModel

class FinancialData(BaseModel):
    """Financial data model for budget vs actuals"""
    department: str
    account_code: str
    account_name: str
    period: str  # YYYY-MM
    budget_amount: float
    actual_amount: float
    variance_amount: float
    variance_percentage: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "department": "Marketing",
                "account_code": "5000",
                "account_name": "Advertising Expense",
                "period": "2024-01",
                "budget_amount": 50000.0,
                "actual_amount": 55000.0,
                "variance_amount": 5000.0,
                "variance_percentage": 10.0
            }
        }

class DataLoader:
    """Loads financial data from various sources"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def load_csv_data(self, filepath: str) -> List[FinancialData]:
        """Load financial data from CSV"""
        df = pd.read_csv(filepath)
        financial_data = []
        
        for _, row in df.iterrows():
            variance_amount = row.get('actual_amount', 0) - row.get('budget_amount', 0)
            variance_percentage = (variance_amount / row.get('budget_amount', 1)) * 100
            
            data = FinancialData(
                department=row.get('department', 'Unknown'),
                account_code=row.get('account_code', '0000'),
                account_name=row.get('account_name', 'Unknown Account'),
                period=row.get('period', datetime.now().strftime('%Y-%m')),
                budget_amount=float(row.get('budget_amount', 0)),
                actual_amount=float(row.get('actual_amount', 0)),
                variance_amount=float(variance_amount),
                variance_percentage=float(variance_percentage)
            )
            financial_data.append(data)
            
        return financial_data
    
    def load_json_data(self, filepath: str) -> List[FinancialData]:
        """Load financial data from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        financial_data = []
        for item in data:
            variance_amount = item.get('actual_amount', 0) - item.get('budget_amount', 0)
            variance_percentage = (variance_amount / item.get('budget_amount', 1)) * 100
            
            data_obj = FinancialData(
                department=item.get('department', 'Unknown'),
                account_code=item.get('account_code', '0000'),
                account_name=item.get('account_name', 'Unknown Account'),
                period=item.get('period', datetime.now().strftime('%Y-%m')),
                budget_amount=float(item.get('budget_amount', 0)),
                actual_amount=float(item.get('actual_amount', 0)),
                variance_amount=float(variance_amount),
                variance_percentage=float(variance_percentage)
            )
            financial_data.append(data_obj)
            
        return financial_data
    
    def generate_sample_data(self) -> List[FinancialData]:
        """Generate sample financial data for testing"""
        departments = ["Marketing", "Sales", "R&D", "Operations", "IT"]
        accounts = [
            {"code": "5000", "name": "Advertising Expense"},
            {"code": "5100", "name": "Travel Expense"},
            {"code": "5200", "name": "Software License"},
            {"code": "5300", "name": "Consulting Fees"},
            {"code": "5400", "name": "Office Supplies"},
        ]
        
        sample_data = []
        current_period = datetime.now().strftime('%Y-%m')
        
        for dept in departments:
            for account in accounts:
                budget = np.random.uniform(10000, 100000)
                actual = budget * np.random.uniform(0.8, 1.2)  # +/- 20% variance
                variance = actual - budget
                variance_pct = (variance / budget) * 100
                
                data = FinancialData(
                    department=dept,
                    account_code=account["code"],
                    account_name=account["name"],
                    period=current_period,
                    budget_amount=round(budget, 2),
                    actual_amount=round(actual, 2),
                    variance_amount=round(variance, 2),
                    variance_percentage=round(variance_pct, 2)
                )
                sample_data.append(data)
                
        return sample_data
    
    def save_financial_data(self, data: List[FinancialData], filename: str):
        """Save financial data to JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        data_dict = [item.model_dump() for item in data]
        
        with open(filepath, 'w') as f:
            json.dump(data_dict, f, indent=2)
            
        print(f"Data saved to {filepath}")
        