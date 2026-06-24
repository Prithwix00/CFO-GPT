from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Generates recommendations based on analysis results"""
    
    def __init__(self):
        self.recommendation_templates = {
            'cost_reduction': [
                "Consider renegotiating contracts for {account_name} in {department} to reduce costs by ~{savings_pct:.1f}%",
                "Implement spending controls for {account_name} in {department} to prevent budget overruns",
                "Review and optimize recurring expenses for {account_name} in {department}"
            ],
            'process_improvement': [
                "Improve approval workflow for {account_name} expenses in {department}",
                "Implement real-time spending alerts for {account_name} in {department}",
                "Enhance budget forecasting methodology for {department}"
            ],
            'budget_adjustment': [
                "Adjust annual budget for {account_name} in {department} by ${adjustment:,.0f} ({adjustment_pct:.1f}%)",
                "Reallocate budget from under-performing areas in {department} to {account_name}",
                "Create contingency budget for {account_name} in {department}"
            ],
            'investigation': [
                "Investigate root cause of {variance_pct:.1f}% variance in {account_name}",
                "Review supporting documents for {account_name} expenses in {department}",
                "Conduct detailed spend analysis for {department}"
            ]
        }
    
    def generate_recommendations(self, 
                                variance_analysis: Dict,
                                trend_analysis: Optional[Dict] = None,
                                investigation_results: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations"""
        
        recommendations = []
        
        # Generate recommendations from variance analysis
        if variance_analysis:
            recs_from_variance = self._generate_variance_recommendations(variance_analysis)
            recommendations.extend(recs_from_variance)
        
        # Generate recommendations from trend analysis
        if trend_analysis:
            recs_from_trend = self._generate_trend_recommendations(trend_analysis)
            recommendations.extend(recs_from_trend)
        
        # Generate recommendations from investigation results
        if investigation_results:
            recs_from_investigation = self._generate_investigation_recommendations(investigation_results)
            recommendations.extend(recs_from_investigation)
        
        # Remove duplicates and sort by priority
        unique_recommendations = self._deduplicate_recommendations(recommendations)
        prioritized_recommendations = self._prioritize_recommendations(unique_recommendations)
        
        return prioritized_recommendations
    
    def _generate_variance_recommendations(self, variance_analysis: Dict) -> List[Dict]:
        """Generate recommendations based on variance analysis"""
        
        recommendations = []
        
        # Check for overall variance
        overall_metrics = variance_analysis.get('overall_metrics', {})
        total_variance_pct = overall_metrics.get('total_variance_pct', 0)
        
        if abs(total_variance_pct) > 5:  # Significant overall variance
            recommendations.append({
                'type': 'budget_adjustment',
                'priority': 'HIGH',
                'recommendation': f"Overall budget variance of {total_variance_pct:.1f}% requires budget recalibration",
                'department': 'ALL',
                'expected_impact': f"Align budget with actual spend by ${overall_metrics.get('total_variance', 0):,.0f}",
                'timeline': 'Next quarter',
                'confidence': 0.8
            })
        
        # Check department-level variances
        dept_analysis = variance_analysis.get('department_analysis', [])
        for dept_data in dept_analysis:
            dept = dept_data.get('department')
            dept_variance_pct = dept_data.get('variance_percentage', 0)
            dept_variance_amt = dept_data.get('variance_amount', 0)
            
            if abs(dept_variance_pct) > 10:  # Significant department variance
                rec_type = 'cost_reduction' if dept_variance_amt > 0 else 'budget_adjustment'
                
                recommendations.append({
                    'type': rec_type,
                    'priority': 'HIGH',
                    'recommendation': f"Address {abs(dept_variance_pct):.1f}% variance in {dept} department",
                    'department': dept,
                    'expected_impact': f"Potential savings/adjustment of ${abs(dept_variance_amt):,.0f}",
                    'timeline': 'Immediate',
                    'confidence': 0.7
                })
        
        # Check for specific account variances
        top_variances = variance_analysis.get('top_variances', {})
        
        for variance in top_variances.get('largest_over_budget', [])[:3]:
            recommendations.append({
                'type': 'investigation',
                'priority': 'HIGH',
                'recommendation': f"Investigate ${variance.get('variance_amount', 0):,.0f} "
                                f"over-budget spend on {variance.get('account_name')}",
                'department': variance.get('department'),
                'expected_impact': 'Identify root cause and prevent recurrence',
                'timeline': '2 weeks',
                'confidence': 0.9
            })
        
        for variance in top_variances.get('largest_under_budget', [])[:2]:
            recommendations.append({
                'type': 'budget_adjustment',
                'priority': 'MEDIUM',
                'recommendation': f"Reallocate unused budget of ${abs(variance.get('variance_amount', 0)):,.0f} "
                                f"from {variance.get('account_name')}",
                'department': variance.get('department'),
                'expected_impact': 'Optimize budget allocation',
                'timeline': 'Next planning cycle',
                'confidence': 0.6
            })
        
        return recommendations
    
    def _generate_trend_recommendations(self, trend_analysis: Dict) -> List[Dict]:
        """Generate recommendations based on trend analysis"""
        
        recommendations = []
        
        trend_detection = trend_analysis.get('trend_detection', {})
        direction = trend_detection.get('direction', 'stable')
        strength = trend_detection.get('strength', 'weak')
        
        if direction != 'stable' and strength in ['strong', 'moderate']:
            if direction == 'upward':
                recommendations.append({
                    'type': 'budget_adjustment',
                    'priority': 'MEDIUM',
                    'recommendation': f"Adjust budget upward to match {direction} spending trend",
                    'department': 'ALL',
                    'expected_impact': 'Prevent future budget variances',
                    'timeline': 'Next fiscal year',
                    'confidence': 0.7
                })
            else:  # downward
                recommendations.append({
                    'type': 'cost_reduction',
                    'priority': 'LOW',
                    'recommendation': f"Leverage {direction} spending trend for cost optimization",
                    'department': 'ALL',
                    'expected_impact': 'Identify areas for permanent cost reduction',
                    'timeline': 'Ongoing',
                    'confidence': 0.6
                })
        
        # Seasonality recommendations
        seasonality = trend_analysis.get('seasonality_analysis', {})
        high_season = seasonality.get('high_season_months', [])
        
        if high_season:
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            high_season_names = [month_names[m-1] for m in high_season[:3]]
            
            recommendations.append({
                'type': 'process_improvement',
                'priority': 'MEDIUM',
                'recommendation': f"Implement seasonal budgeting for high-spend months: {', '.join(high_season_names)}",
                'department': 'ALL',
                'expected_impact': 'Improve budget accuracy',
                'timeline': 'Next seasonal cycle',
                'confidence': 0.8
            })
        
        # Anomaly recommendations
        anomalies = trend_analysis.get('anomalies', [])
        if anomalies:
            recent_anomalies = [a for a in anomalies if 
                               datetime.strptime(a.get('period', '2000-01'), '%Y-%m') > 
                               datetime.now().replace(day=1) - pd.DateOffset(months=3)]
            
            if recent_anomalies:
                recommendations.append({
                    'type': 'investigation',
                    'priority': 'HIGH',
                    'recommendation': f"Investicate {len(recent_anomalies)} recent spending anomalies",
                    'department': 'ALL',
                    'expected_impact': 'Prevent irregular spending patterns',
                    'timeline': '1 month',
                    'confidence': 0.9
                })
        
        return recommendations
    
    def _generate_investigation_recommendations(self, investigation_results: List[Dict]) -> List[Dict]:
        """Generate recommendations based on investigation results"""
        
        recommendations = []
        
        for result in investigation_results:
            variance = result.get('variance_details', {})
            dept = result.get('department', 'Unknown')
            account = variance.get('account_name', 'Unknown')
            variance_amt = variance.get('variance_amount', 0)
            variance_pct = variance.get('variance_percentage', 0)
            
            investigation = result.get('investigation_result', {})
            confidence = investigation.get('confidence', 0)
            
            if confidence > 70:  # High confidence findings
                recommendations.append({
                    'type': 'budget_adjustment',
                    'priority': 'HIGH',
                    'recommendation': f"Adjust {account} budget in {dept} based on investigation findings",
                    'department': dept,
                    'expected_impact': f"Correct ${abs(variance_amt):,.0f} variance",
                    'timeline': 'Next month',
                    'confidence': confidence / 100
                })
            else:  # Lower confidence - need more investigation
                recommendations.append({
                    'type': 'investigation',
                    'priority': 'MEDIUM',
                    'recommendation': f"Conduct deeper investigation into {account} variance in {dept}",
                    'department': dept,
                    'expected_impact': 'Gather additional evidence',
                    'timeline': '3 weeks',
                    'confidence': 0.5
                })
            
            # Add specific recommendations from investigation
            inv_recommendations = result.get('recommendations', [])
            for rec in inv_recommendations[:2]:  # Take top 2
                recommendations.append({
                    'type': 'process_improvement',
                    'priority': rec.get('priority', 'MEDIUM'),
                    'recommendation': rec.get('action', ''),
                    'department': dept,
                    'expected_impact': rec.get('impact', ''),
                    'timeline': rec.get('timeline', '1 month'),
                    'confidence': 0.7
                })
        
        return recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Remove duplicate recommendations"""
        
        seen = set()
        unique_recommendations = []
        
        for rec in recommendations:
            # Create a key based on recommendation text and department
            rec_key = (rec['recommendation'][:100], rec['department'])
            
            if rec_key not in seen:
                seen.add(rec_key)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _prioritize_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Sort recommendations by priority and impact"""
        
        priority_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        
        def sort_key(rec):
            priority_score = priority_order.get(rec.get('priority', 'LOW'), 0)
            confidence = rec.get('confidence', 0)
            
            # Higher priority and confidence first
            return (-priority_score, -confidence)
        
        sorted_recommendations = sorted(recommendations, key=sort_key)
        
        # Limit to top 10 recommendations
        return sorted_recommendations[:10]
    
    def create_implementation_plan(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Create an implementation plan for recommendations"""
        
        if not recommendations:
            return {"message": "No recommendations to implement"}
        
        # Group by department
        dept_plans = {}
        for rec in recommendations:
            dept = rec.get('department', 'General')
            
            if dept not in dept_plans:
                dept_plans[dept] = {
                    'department': dept,
                    'high_priority': [],
                    'medium_priority': [],
                    'low_priority': [],
                    'total_impact': 0
                }
            
            # Add to appropriate priority list
            priority = rec.get('priority', 'MEDIUM').lower()
            if priority + '_priority' in dept_plans[dept]:
                dept_plans[dept][priority + '_priority'].append(rec)
        
        # Create timeline
        timeline = self._create_timeline(recommendations)
        
        # Calculate resource requirements
        resources = self._estimate_resources(recommendations)
        
        # Generate executive summary
        summary = self._generate_implementation_summary(recommendations, dept_plans)
        
        return {
            'total_recommendations': len(recommendations),
            'department_plans': list(dept_plans.values()),
            'timeline': timeline,
            'resource_requirements': resources,
            'executive_summary': summary,
            'success_metrics': self._define_success_metrics(recommendations)
        }
    
    def _create_timeline(self, recommendations: List[Dict]) -> List[Dict]:
        """Create implementation timeline"""
        
        timeline = []
        current_date = datetime.now()
        
        # Define phases
        phases = [
            {'name': 'Immediate (0-30 days)', 'duration_days': 30},
            {'name': 'Short-term (1-3 months)', 'duration_days': 60},
            {'name': 'Medium-term (3-6 months)', 'duration_days': 90},
            {'name': 'Long-term (6+ months)', 'duration_days': 180}
        ]
        
        for phase in phases:
            phase_recommendations = []
            
            for rec in recommendations:
                timeline_str = rec.get('timeline', '').lower()
                
                if phase['name'] == 'Immediate (0-30 days)' and 'week' in timeline_str:
                    phase_recommendations.append(rec)
                elif phase['name'] == 'Short-term (1-3 months)' and 'month' in timeline_str:
                    phase_recommendations.append(rec)
                elif phase['name'] == 'Medium-term (3-6 months)' and any(word in timeline_str 
                                                                        for word in ['quarter', '3 month', '90']):
                    phase_recommendations.append(rec)
                elif phase['name'] == 'Long-term (6+ months)':
                    phase_recommendations.append(rec)
            
            if phase_recommendations:
                timeline.append({
                    'phase': phase['name'],
                    'start_date': current_date.strftime('%Y-%m-%d'),
                    'end_date': (current_date + pd.DateOffset(days=phase['duration_days'])).strftime('%Y-%m-%d'),
                    'recommendations': [r['recommendation'] for r in phase_recommendations[:3]],
                    'count': len(phase_recommendations)
                })
            
            current_date += pd.DateOffset(days=phase['duration_days'])
        
        return timeline
    
    def _estimate_resources(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Estimate resource requirements"""
        
        # Simple estimation based on recommendation count and types
        high_priority = sum(1 for r in recommendations if r.get('priority') == 'HIGH')
        medium_priority = sum(1 for r in recommendations if r.get('priority') == 'MEDIUM')
        
        total_effort_days = (high_priority * 5) + (medium_priority * 3) + \
                           (len(recommendations) - high_priority - medium_priority) * 2
        
        return {
            'estimated_person_days': total_effort_days,
            'team_size_recommended': min(3, max(1, total_effort_days // 20)),
            'key_roles': ['FP&A Analyst', 'Department Head', 'Finance Controller'],
            'estimated_duration_weeks': max(4, total_effort_days // 5 // 3)  # 3 days per week
        }
    
    def _generate_implementation_summary(self, 
                                        recommendations: List[Dict],
                                        dept_plans: Dict) -> str:
        """Generate implementation summary"""
        
        high_priority = sum(1 for r in recommendations if r.get('priority') == 'HIGH')
        departments = list(dept_plans.keys())
        
        return f"""Implementation Plan Summary:

Total Recommendations: {len(recommendations)}
High Priority Actions: {high_priority}
Departments Involved: {len(departments)}

Key Focus Areas:
1. Immediate actions for {high_priority} critical variances
2. Department-specific plans for {', '.join(departments[:3])}{' and more' if len(departments) > 3 else ''}
3. Process improvements to prevent future variances

Expected Outcomes:
- Improved budget accuracy
- Reduced variance investigation time
- Enhanced financial controls

Success will be measured by reduction in significant variances and improved forecast accuracy."""
    
    def _define_success_metrics(self, recommendations: List[Dict]) -> List[Dict]:
        """Define success metrics for recommendations"""
        
        metrics = [
            {
                'metric': 'Variance Reduction',
                'target': 'Reduce significant variances by 50%',
                'measurement': 'Monthly variance analysis',
                'timeline': '6 months'
            },
            {
                'metric': 'Budget Accuracy',
                'target': 'Improve budget vs actual accuracy to within 5%',
                'measurement': 'Quarterly review',
                'timeline': '1 year'
            },
            {
                'metric': 'Investigation Time',
                'target': 'Reduce variance investigation time by 60%',
                'measurement': 'Average time per investigation',
                'timeline': '3 months'
            },
            {
                'metric': 'Recommendation Implementation',
                'target': 'Implement 80% of high-priority recommendations',
                'measurement': 'Quarterly progress review',
                'timeline': '1 year'
            }
        ]
        
        return metrics