from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VarianceEngine:
    """Engine for calculating and analyzing variances"""
    
    def __init__(self, variance_threshold: float = 0.10, significant_amount: float = 10000):
        self.variance_threshold = variance_threshold
        self.significant_amount = significant_amount
    
    def calculate_variances(self, budget_data: List[Dict], actual_data: List[Dict]) -> List[Dict]:
        """Calculate variances between budget and actual data"""
        
        variances = []
        
        # Create dictionaries for easy lookup
        budget_dict = {(item.get('department'), item.get('account_code'), item.get('period')): item 
                      for item in budget_data}
        actual_dict = {(item.get('department'), item.get('account_code'), item.get('period')): item 
                      for item in actual_data}
        
        # Find matching records
        all_keys = set(budget_dict.keys()) | set(actual_dict.keys())
        
        for key in all_keys:
            dept, account, period = key
            
            budget_item = budget_dict.get(key, {})
            actual_item = actual_dict.get(key, {})
            
            budget_amount = budget_item.get('amount', 0)
            actual_amount = actual_item.get('amount', 0)
            
            variance_amount = actual_amount - budget_amount
            variance_percentage = (variance_amount / budget_amount * 100) if budget_amount != 0 else 0
            
            variance_data = {
                'department': dept,
                'account_code': account,
                'account_name': budget_item.get('account_name', actual_item.get('account_name', 'Unknown')),
                'period': period,
                'budget_amount': budget_amount,
                'actual_amount': actual_amount,
                'variance_amount': variance_amount,
                'variance_percentage': variance_percentage,
                'is_significant': self._is_significant_variance(variance_amount, variance_percentage),
                'significance_reason': self._get_significance_reason(variance_amount, variance_percentage)
            }
            
            variances.append(variance_data)
        
        return variances
    
    def _is_significant_variance(self, variance_amount: float, variance_percentage: float) -> bool:
        """Check if variance is significant based on thresholds"""
        abs_amount = abs(variance_amount)
        abs_percentage = abs(variance_percentage)
        
        return (abs_amount >= self.significant_amount or 
                abs_percentage >= (self.variance_threshold * 100))
    
    def _get_significance_reason(self, variance_amount: float, variance_percentage: float) -> str:
        """Get reason for variance significance"""
        reasons = []
        abs_amount = abs(variance_amount)
        abs_percentage = abs(variance_percentage)
        
        if abs_amount >= self.significant_amount:
            reasons.append(f"Amount (${abs_amount:,.2f}) ≥ ${self.significant_amount:,.2f}")
        
        if abs_percentage >= (self.variance_threshold * 100):
            reasons.append(f"Percentage ({abs_percentage:.1f}%) ≥ {self.variance_threshold*100:.1f}%")
        
        return "; ".join(reasons) if reasons else "Within acceptable limits"
    
    def analyze_variance_patterns(self, variances: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in variances"""
        
        if not variances:
            return {"error": "No variance data provided"}
        
        df = pd.DataFrame(variances)
        
        # Overall metrics
        total_budget = df['budget_amount'].sum()
        total_actual = df['actual_amount'].sum()
        total_variance = df['variance_amount'].sum()
        total_variance_pct = (total_variance / total_budget * 100) if total_budget != 0 else 0
        
        # Department analysis
        dept_analysis = df.groupby('department').agg({
            'budget_amount': 'sum',
            'actual_amount': 'sum',
            'variance_amount': 'sum',
            'variance_percentage': 'mean',
            'is_significant': 'sum'
        }).reset_index()
        
        dept_analysis['variance_percentage'] = (dept_analysis['variance_amount'] / 
                                                dept_analysis['budget_amount'] * 100)
        
        # Account analysis
        account_analysis = df.groupby(['department', 'account_name']).agg({
            'variance_amount': 'sum',
            'is_significant': 'sum'
        }).reset_index()
        
        # Time analysis
        if 'period' in df.columns:
            df['period_date'] = pd.to_datetime(df['period'] + '-01', format='%Y-%m-%d', errors='coerce')
            time_analysis = df.groupby(pd.Grouper(key='period_date', freq='M')).agg({
                'budget_amount': 'sum',
                'actual_amount': 'sum',
                'variance_amount': 'sum',
                'is_significant': 'sum'
            }).reset_index()
            time_analysis['period'] = time_analysis['period_date'].dt.strftime('%Y-%m')
        else:
            time_analysis = None
        
        # Top variances
        top_over_budget = df.nlargest(5, 'variance_amount')[['department', 'account_name', 'variance_amount']]
        top_under_budget = df.nsmallest(5, 'variance_amount')[['department', 'account_name', 'variance_amount']]
        
        # Significance analysis
        significant_count = df['is_significant'].sum()
        significance_rate = (significant_count / len(df) * 100) if len(df) > 0 else 0
        
        return {
            'overall_metrics': {
                'total_budget': total_budget,
                'total_actual': total_actual,
                'total_variance': total_variance,
                'total_variance_pct': total_variance_pct,
                'total_accounts': len(df),
                'significant_accounts': significant_count,
                'significance_rate': significance_rate
            },
            'department_analysis': dept_analysis.to_dict('records'),
            'account_analysis': account_analysis.to_dict('records'),
            'time_analysis': time_analysis.to_dict('records') if time_analysis is not None else [],
            'top_variances': {
                'largest_over_budget': top_over_budget.to_dict('records'),
                'largest_under_budget': top_under_budget.to_dict('records')
            },
            'summary_statistics': {
                'avg_variance_pct': df['variance_percentage'].mean(),
                'std_variance_pct': df['variance_percentage'].std(),
                'max_over_budget': df['variance_amount'].max(),
                'max_under_budget': df['variance_amount'].min(),
                'median_variance': df['variance_amount'].median()
            }
        }
    
    def forecast_future_variances(self, historical_variances: List[Dict], periods: int = 3) -> Dict[str, Any]:
        """Forecast future variances based on historical data"""
        
        if not historical_variances:
            return {"error": "No historical data provided"}
        
        df = pd.DataFrame(historical_variances)
        
        # Ensure period column exists and is datetime
        if 'period' not in df.columns:
            return {"error": "Period column not found"}
        
        df['period'] = pd.to_datetime(df['period'] + '-01', format='%Y-%m-%d', errors='coerce')
        df = df.sort_values('period')
        
        # Group by period
        period_data = df.groupby('period').agg({
            'budget_amount': 'sum',
            'actual_amount': 'sum',
            'variance_amount': 'sum'
        }).reset_index()
        
        # Simple linear regression for forecasting
        if len(period_data) >= 2:
            x = np.arange(len(period_data))
            y = period_data['variance_amount'].values
            
            # Linear regression
            coeff = np.polyfit(x, y, 1)
            
            # Forecast future periods
            last_date = period_data['period'].iloc[-1]
            forecast_dates = []
            forecast_values = []
            
            for i in range(1, periods + 1):
                forecast_date = last_date + pd.DateOffset(months=i)
                forecast_value = coeff[0] * (len(period_data) + i - 1) + coeff[1]
                
                forecast_dates.append(forecast_date.strftime('%Y-%m'))
                forecast_values.append(float(forecast_value))
        else:
            # Not enough data for regression
            avg_variance = period_data['variance_amount'].mean() if len(period_data) > 0 else 0
            last_date = period_data['period'].iloc[-1] if len(period_data) > 0 else pd.Timestamp.now()
            
            forecast_dates = []
            forecast_values = []
            
            for i in range(1, periods + 1):
                forecast_date = last_date + pd.DateOffset(months=i)
                forecast_dates.append(forecast_date.strftime('%Y-%m'))
                forecast_values.append(float(avg_variance))
        
        return {
            'historical_trend': period_data.to_dict('records'),
            'forecast': {
                'periods': forecast_dates,
                'predicted_variances': forecast_values,
                'confidence_interval': self._calculate_confidence_interval(forecast_values)
            },
            'trend_analysis': {
                'trend_direction': 'upward' if coeff[0] > 0 else 'downward' if coeff[0] < 0 else 'stable',
                'trend_strength': abs(coeff[0]) if 'coeff' in locals() else 0,
                'forecast_accuracy': self._estimate_accuracy(period_data['variance_amount'].values)
            }
        }
    
    def _calculate_confidence_interval(self, values: List[float]) -> List[float]:
        """Calculate simple confidence interval"""
        if not values:
            return [0, 0]
        
        mean = np.mean(values)
        std = np.std(values) if len(values) > 1 else 0
        
        return [float(mean - 1.96 * std), float(mean + 1.96 * std)]
    
    def _estimate_accuracy(self, historical_values: np.ndarray) -> float:
        """Estimate forecast accuracy based on historical volatility"""
        if len(historical_values) < 2:
            return 0.0
        
        # Simple accuracy measure based on coefficient of variation
        mean_abs = np.mean(np.abs(historical_values))
        std_abs = np.std(np.abs(historical_values))
        
        if mean_abs == 0:
            return 100.0
        
        cv = std_abs / mean_abs
        accuracy = max(0.0, 100.0 * (1.0 - cv))
        
        return float(accuracy)