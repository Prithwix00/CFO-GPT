# src/workflows/fpa_workflow.py
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.agents.monitor_agent import MonitorAgent
from src.agents.investigator import InvestigatorAgent
from src.agents.reporter_agent import ReporterAgent
from src.rag.retriever import RAGRetriever

logger = logging.getLogger(__name__)

class FPAWorkflow:
    """Main FP&A workflow orchestrator"""
    
    def __init__(self, 
                 monitor_agent: MonitorAgent,
                 investigator_agent: InvestigatorAgent,
                 reporter_agent: ReporterAgent,
                 rag_retriever: RAGRetriever):
        self.monitor_agent = monitor_agent
        self.investigator_agent = investigator_agent
        self.reporter_agent = reporter_agent
        self.rag_retriever = rag_retriever
        
    def run(self, 
            financial_data: List[Dict],
            documents: List = None,
            department_filter: str = None) -> Dict[str, Any]:
        """Run the complete FP&A workflow"""
        start_time = datetime.now()
        results = {
            "status": "running",
            "metrics": {
                "total_variances_analyzed": 0,
                "significant_variances_found": 0,
                "investigations_completed": 0,
                "proposals_generated": 0,
                "recommendations_generated": 0,
                "processing_time": ""
            },
            "results": {
                "variance_analysis": {},
                "investigation_results": [],
                "budget_proposals": [],
                "recommendations": [],
                "executive_summary": {}
            },
            "errors": []
        }
        
        try:
            logger.info("Starting FP&A workflow...")
            
            # Step 1: Detect variances
            logger.info("Starting variance detection...")
            variance_analysis = self._detect_variances(financial_data, department_filter)
            results["results"]["variance_analysis"] = variance_analysis
            results["metrics"]["total_variances_analyzed"] = len(variance_analysis.get("all_variances", []))
            results["metrics"]["significant_variances_found"] = len(variance_analysis.get("significant_variances", []))
            
            if not variance_analysis.get("significant_variances"):
                logger.warning("No significant variances found. Ending workflow.")
                results["status"] = "completed"
                results["metrics"]["processing_time"] = self._get_processing_time(start_time)
                return results
            
            # Step 2: Investigate significant variances
            logger.info("Starting variance investigation...")
            investigation_results = self._investigate_variances(variance_analysis["significant_variances"])
            results["results"]["investigation_results"] = investigation_results
            
            # Count successful investigations
            successful_investigations = [r for r in investigation_results if r.get("status") == "SUCCESS"]
            results["metrics"]["investigations_completed"] = len(successful_investigations)
            
            # Step 3: Generate budget proposals and recommendations
            logger.info("Creating budget proposals and recommendations...")
            budget_proposals = []
            recommendations = []
            
            for investigation in successful_investigations:
                # Generate budget proposal
                if investigation.get('variance_details'):
                    proposal = self._generate_budget_proposal(investigation)
                    if proposal and proposal.get('status') == 'SUCCESS':
                        budget_proposals.append(proposal)
                    
                    # Generate recommendation
                    recommendation = self._generate_recommendation(investigation)
                    if recommendation:
                        recommendations.append(recommendation)
            
            results["results"]["budget_proposals"] = budget_proposals
            results["results"]["recommendations"] = recommendations
            results["metrics"]["proposals_generated"] = len(budget_proposals)
            results["metrics"]["recommendations_generated"] = len(recommendations)
            
            logger.info(f"Generated {len(budget_proposals)} budget proposals and {len(recommendations)} recommendations")
            
            # Step 4: Generate executive summary
            if successful_investigations:
                logger.info("Generating executive summary...")
                executive_summary = self.reporter_agent.generate_executive_summary(successful_investigations)
                results["results"]["executive_summary"] = executive_summary
                
                # Generate detailed reports for top 3 investigations
                logger.info("Generating detailed reports...")
                for investigation in successful_investigations[:3]:
                    try:
                        report = self.reporter_agent.generate_detailed_report(investigation)
                        if report.get('status') == 'SUCCESS':
                            logger.info(f"Generated detailed report for {report.get('department')} - {report.get('account')}")
                    except Exception as e:
                        logger.error(f"Error generating detailed report: {e}")
            
            results["status"] = "completed"
            results["metrics"]["processing_time"] = self._get_processing_time(start_time)
            logger.info("FP&A workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["metrics"]["processing_time"] = self._get_processing_time(start_time)
        
        return results
    
    def _detect_variances(self, financial_data: List[Dict], department_filter: str = None) -> Dict[str, Any]:
        """Detect variances in financial data"""
        try:
            # Filter by department if specified
            if department_filter:
                filtered_data = [
                    record for record in financial_data
                    if self._get_record_value(record, 'department', '').lower() == department_filter.lower()
                ]
                if not filtered_data:
                    logger.warning(f"No data found for department: {department_filter}")
                    return {"all_variances": [], "significant_variances": []}
                financial_data = filtered_data
            
            # Detect variances
            variance_results = self.monitor_agent.detect_variances(financial_data)
            
            if not variance_results:
                return {"all_variances": [], "significant_variances": []}
            
            # Get significant variances
            all_variances = variance_results.get("all_variances", variance_results.get("total_analysis", []))
            significant_variances = variance_results.get("significant_variances", [])
            
            if significant_variances:
                logger.info(f"Detected {len(significant_variances)} significant variances")
                logger.info("Top variances found:")
                for i, variance in enumerate(significant_variances[:5], 1):
                    dept = variance.get('department', 'Unknown')
                    account = variance.get('account_name', 'Unknown')
                    amount = variance.get('variance_amount', 0)
                    percent = variance.get('variance_percentage', 0)
                    logger.info(f"  {i}. {dept} - {account}: ${amount:,.2f} ({percent:.1f}%)")
            
            return {
                "all_variances": all_variances,
                "significant_variances": significant_variances,
                "metrics": variance_results.get("metrics", {})
            }
            
        except Exception as e:
            logger.error(f"Error detecting variances: {e}")
            return {"all_variances": [], "significant_variances": []}

    def _get_record_value(self, record: Any, key: str, default: Any = None) -> Any:
        """Read a value from either a dict or a Pydantic/data object."""
        if isinstance(record, dict):
            return record.get(key, default)
        return getattr(record, key, default)
    
    def _investigate_variances(self, significant_variances: List[Dict]) -> List[Dict]:
        """Investigate each significant variance"""
        investigation_results = []
        
        logger.info(f"Investigating {len(significant_variances)} variances:")
        for i, variance in enumerate(significant_variances, 1):
            try:
                dept = variance.get('department', 'Unknown')
                account = variance.get('account_name', 'Unknown')
                amount = variance.get('variance_amount', 0)
                
                logger.info(f"Investigating variance {i}/{len(significant_variances)}")
                logger.info(f"  Department: {dept}")
                logger.info(f"  Account: {account}")
                logger.info(f"  Variance: ${amount:,.2f}")
                
                # Investigate the variance
                investigation_result = self.investigator_agent.investigate_variance(
                    variance_details=variance,
                    department=dept
                )
                
                if investigation_result and investigation_result.get("status") == "SUCCESS":
                    # Add variance details to investigation result
                    investigation_result["variance_details"] = variance
                    investigation_result["department"] = dept
                    
                    # Log evidence found
                    evidence_count = investigation_result.get("evidence_found", 0)
                    if evidence_count > 0:
                        logger.info(f"    Found {evidence_count} supporting documents")
                        evidence_summary = investigation_result.get("evidence_summary", "")
                        if len(evidence_summary) > 100:
                            evidence_summary = evidence_summary[:100] + "..."
                        logger.info(f"    Evidence: {evidence_summary}")
                    
                    investigation_results.append(investigation_result)
                else:
                    logger.warning(f"    Investigation failed: {investigation_result.get('error', 'Unknown error')}")
                    # Still add with error status
                    investigation_results.append({
                        "variance_details": variance,
                        "department": dept,
                        "status": "ERROR",
                        "error": investigation_result.get('error', 'Unknown error'),
                        "evidence_found": 0
                    })
                    
            except Exception as e:
                logger.error(f"Error investigating variance {i}: {e}")
                investigation_results.append({
                    "variance_details": variance,
                    "department": variance.get('department', 'Unknown'),
                    "status": "ERROR",
                    "error": str(e),
                    "evidence_found": 0
                })
        
        logger.info(f"Completed {len(investigation_results)} investigations")
        return investigation_results
    
    def _generate_budget_proposal(self, investigation_result: Dict) -> Optional[Dict]:
        """Generate budget proposal for an investigation"""
        try:
            variance_details = investigation_result.get("variance_details", {})
            department = investigation_result.get("department", "Unknown")
            investigation_data = investigation_result.get("investigation_result", {})
            
            if not variance_details or not department:
                logger.warning("Missing variance details or department for budget proposal")
                return None
            
            # Generate budget proposal
            proposal = self.reporter_agent.generate_budget_adjustment_proposal(
                variance_details=variance_details,
                investigation_result=investigation_data,
                department=department
            )
            
            return proposal
            
        except Exception as e:
            logger.error(f"Error generating budget proposal: {e}")
            return None
    
    def _generate_recommendation(self, investigation_result: Dict) -> Optional[Dict]:
        """Generate recommendation from investigation"""
        try:
            variance = investigation_result.get("variance_details", {})
            department = investigation_result.get("department", "Unknown")
            account = variance.get("account_name", "Unknown")
            amount = variance.get("variance_amount", 0)
            investigation_data = investigation_result.get("investigation_result", {})
            
            # Get investigation analysis for context
            root_cause = investigation_data.get("root_cause_analysis", "")
            evidence_count = investigation_result.get("evidence_found", 0)
            
            # Determine priority based on variance amount and evidence
            abs_amount = abs(amount)
            if abs_amount > 20000:
                priority = "HIGH"
            elif abs_amount > 10000:
                priority = "MEDIUM"
            else:
                priority = "LOW"
            
            # Generate specific recommendation based on investigation findings
            if "insufficient evidence" in root_cause.lower():
                action = f"Gather additional documentation for ${abs(amount):,.0f} {account} variance in {department}"
            elif "contract" in root_cause.lower() or "agreement" in root_cause.lower():
                action = f"Review and update contract terms for {account} in {department}"
            elif "invoice" in root_cause.lower() or "payment" in root_cause.lower():
                action = f"Verify invoice processing and approvals for {account} in {department}"
            elif "license" in root_cause.lower() or "software" in root_cause.lower():
                action = f"Assess software license needs and renewals for {account} in {department}"
            elif "travel" in root_cause.lower():
                action = f"Review travel policies and approvals for {department}"
            elif "advertising" in root_cause.lower() or "marketing" in root_cause.lower():
                action = f"Evaluate marketing campaign ROI for {account} in {department}"
            elif "consulting" in root_cause.lower():
                action = f"Review consulting service agreements for {department}"
            else:
                # Generic but specific recommendation
                if amount > 0:
                    action = f"Address ${abs_amount:,.0f} overspend in {account} for {department}"
                else:
                    action = f"Optimize ${abs_amount:,.0f} underspend in {account} for {department}"
            
            # Create recommendation
            recommendation = {
                "action": action,
                "priority": priority,
                "owner": f"{department} Manager",
                "timeline": "Within 2 weeks",
                "impact": f"Address ${abs_amount:,.0f} variance",
                "details": root_cause[:200] if root_cause else f"{evidence_count} supporting documents found",
                "department": department,
                "account": account,
                "variance_amount": amount
            }
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return None
    
    def _get_processing_time(self, start_time: datetime) -> str:
        """Calculate and format processing time"""
        elapsed = datetime.now() - start_time
        total_seconds = int(elapsed.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
