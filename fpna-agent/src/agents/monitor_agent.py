from typing import List, Dict, Any, Optional
from .base_agent import BaseAgent
from src.utils.data_loader import FinancialData
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class MonitorAgent(BaseAgent):
    """Agent for monitoring budget vs actuals and detecting variances"""
    
    def __init__(self):
        system_prompt = """You are a Financial Planning & Analysis (FP&A) Monitor Agent.
        Your role is to analyze budget vs actuals data and identify significant variances.
        
        Key responsibilities:
        1. Calculate variance amounts and percentages
        2. Identify variances exceeding thresholds (10% or $10,000)
        3. Categorize variances by department and account
        4. Flag high-risk variances for investigation
        
        Be precise, analytical, and focus on material variances that require attention."""
        
        super().__init__("MonitorAgent", system_prompt)
        
    def detect_variances(self, financial_data: List[FinancialData]) -> Dict[str, Any]:
        """Detect significant variances in financial data"""
        
        significant_variances = []
        total_variances = []
        
        for data in financial_data:
            variance_info = {
                "department": data.department,
                "account_code": data.account_code,
                "account_name": data.account_name,
                "period": data.period,
                "budget": data.budget_amount,
                "actual": data.actual_amount,
                "variance_amount": data.variance_amount,
                "variance_percentage": data.variance_percentage,
                "is_significant": False,
                "reason": ""
            }
            
            # Check if variance is significant
            abs_variance_pct = abs(data.variance_percentage)
            abs_variance_amt = abs(data.variance_amount)
            
            is_significant = False
            reasons = []
            
            if abs_variance_pct >= settings.VARIANCE_THRESHOLD * 100:  # Convert to percentage
                is_significant = True
                reasons.append(f"Variance percentage ({abs_variance_pct:.1f}%) exceeds threshold ({settings.VARIANCE_THRESHOLD*100:.1f}%)")
            
            if abs_variance_amt >= settings.SIGNIFICANT_AMOUNT:
                is_significant = True
                reasons.append(f"Variance amount (${abs_variance_amt:,.2f}) exceeds threshold (${settings.SIGNIFICANT_AMOUNT:,.2f})")
            
            if is_significant:
                variance_info["is_significant"] = True
                variance_info["reason"] = "; ".join(reasons)
                significant_variances.append(variance_info)
            
            total_variances.append(variance_info)
        
        # Generate analysis summary
        analysis_summary = self._generate_analysis_summary(
            total_variances=total_variances,
            significant_variances=significant_variances
        )
        
        return {
            "total_analysis": total_variances,
            "significant_variances": significant_variances,
            "summary": analysis_summary,
            "metrics": {
                "total_items": len(total_variances),
                "significant_items": len(significant_variances),
                "significance_rate": len(significant_variances) / len(total_variances) * 100 if total_variances else 0
            }
        }
    
    def _generate_analysis_summary(self, total_variances: List[Dict], significant_variances: List[Dict]) -> str:
        """Generate a summary of variance analysis"""
        
        if not total_variances:
            return "No financial data available for analysis."
        
        # Calculate total metrics
        total_budget = sum(item["budget"] for item in total_variances)
        total_actual = sum(item["actual"] for item in total_variances)
        total_variance = total_actual - total_budget
        total_variance_pct = (total_variance / total_budget * 100) if total_budget else 0
        
        # Group by department
        dept_summary = {}
        for item in total_variances:
            dept = item["department"]
            if dept not in dept_summary:
                dept_summary[dept] = {
                    "count": 0,
                    "significant_count": 0,
                    "total_variance": 0,
                    "items": []
                }
            
            dept_summary[dept]["count"] += 1
            dept_summary[dept]["total_variance"] += item["variance_amount"]
            
            if item["is_significant"]:
                dept_summary[dept]["significant_count"] += 1
        
        # Prepare prompt for LLM summary
        prompt = f"""Based on the following variance analysis, provide a concise executive summary:

Total Analysis:
- Total Budget: ${total_budget:,.2f}
- Total Actual: ${total_actual:,.2f}
- Total Variance: ${total_variance:,.2f} ({total_variance_pct:.1f}%)
- Total Items Analyzed: {len(total_variances)}
- Significant Variances Found: {len(significant_variances)}

Department Summary:
{chr(10).join([f"- {dept}: {data['count']} accounts, {data['significant_count']} significant variances, total variance: ${data['total_variance']:,.2f}" for dept, data in dept_summary.items()])}

Significant Variances (Top 5 by amount):
{chr(10).join([f"- {item['department']} - {item['account_name']}: ${item['variance_amount']:,.2f} ({item['variance_percentage']:.1f}%) - {item['reason']}" for item in sorted(significant_variances, key=lambda x: abs(x['variance_amount']), reverse=True)[:5]])}

Provide a 3-4 paragraph executive summary highlighting:
1. Overall financial performance
2. Key areas of concern (departments/accounts with largest variances)
3. Recommendations for investigation priority
4. Any patterns or trends observed"""

        try:
            summary = self.invoke(prompt)
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback summary
            return f"""
            Variance Analysis Summary:
            
            Overall Performance: Total variance of ${total_variance:,.2f} ({total_variance_pct:.1f}%) 
            against budget of ${total_budget:,.2f}.
            
            Significant Findings: {len(significant_variances)} out of {len(total_variances)} 
            accounts show significant variances exceeding thresholds.
            
            Top Concern Areas: {', '.join(sorted(dept_summary.keys(), key=lambda x: dept_summary[x]['significant_count'], reverse=True)[:3])}
            
            Next Steps: Investigate top {min(5, len(significant_variances))} variances for root causes.
            """