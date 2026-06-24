# src/agents/reporter_agent.py
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from datetime import datetime
import json
import logging
from pathlib import Path
from config.settings import settings

logger = logging.getLogger(__name__)

class ReporterAgent(BaseAgent):
    """Agent for generating reports and executive summaries"""
    
    def __init__(self):
        system_prompt = """You are a Financial Reporting Agent specialized in creating executive reports.
        Your role is to synthesize investigation findings into professional reports.
        
        Key responsibilities:
        1. Create clear, concise executive summaries
        2. Generate detailed investigation reports with evidence citations
        3. Draft specific, justified budget adjustment proposals
        4. Format reports for different stakeholders (CFO, Department Heads, etc.)
        5. Highlight key insights and actionable recommendations
        
        BE SPECIFIC AND DETAILED:
        - Provide comprehensive justifications with complete sentences
        - Include specific numbers and data points
        - Reference evidence documents when applicable
        - Give complete analysis without truncation
        
        IMPORTANT: 
        - Always provide complete, final answers without any thinking process or <think> tags.
        - For budget proposals, be specific about adjustment amounts and provide COMPLETE justification.
        - Use proper business formatting with clear sections and bullet points.
        - Include concrete numbers and specific recommendations.
        - NEVER truncate sentences - always provide complete thoughts."""
        
        super().__init__("ReporterAgent", system_prompt)
        
        # Initialize reports directory
        self.reports_dir = Path(settings.REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 ReporterAgent initialized. Reports will be saved to: {self.reports_dir}")
        logger.info(f"📁 Directory exists: {self.reports_dir.exists()}")
    
    def generate_executive_summary(self, investigation_results: List[Dict]) -> Dict[str, Any]:
        """Generate executive summary for CFO review"""
        
        if not investigation_results:
            return {
                "status": "NO_DATA",
                "summary": "No investigation results to summarize.",
                "key_insights": [],
                "recommendations": [],
                "filepath": None
            }
        
        try:
            # Prepare summary data
            total_variances = len(investigation_results)
            variances_with_evidence = sum(1 for r in investigation_results 
                                       if r.get("evidence_found", 0) > 0)
            
            # Calculate total variance amounts
            total_overspend = 0
            total_underspend = 0
            top_variances = []
            
            for result in investigation_results:
                variance = result.get("variance_details", {})
                if variance:
                    amount = variance.get("variance_amount", 0)
                    if amount > 0:
                        total_overspend += amount
                    else:
                        total_underspend += abs(amount)
                    
                    # Add to top variances
                    top_variances.append({
                        "department": result.get("department", "Unknown"),
                        "account": variance.get("account_name", "Unknown"),
                        "amount": abs(amount),
                        "percentage": variance.get("variance_percentage", 0),
                        "type": "overspend" if amount > 0 else "underspend",
                        "confidence": result.get("investigation_result", {}).get("confidence", 0)
                    })
            
            # Sort by amount
            top_variances.sort(key=lambda x: x["amount"], reverse=True)
            
            prompt = f"""Generate a comprehensive executive summary for FP&A leadership.

INVESTIGATION OVERVIEW:
- Total variances investigated: {total_variances}
- Variances with supporting evidence: {variances_with_evidence}
- Total overspend identified: ${total_overspend:,.2f}
- Total underspend identified: ${total_underspend:,.2f}
- Average investigation confidence: {sum(v['confidence'] for v in top_variances)/len(top_variances) if top_variances else 0:.1f}%

TOP 5 SIGNIFICANT VARIANCES:
{chr(10).join([f"  {i+1}. {v['department']} - {v['account']}: "
                f"${v['amount']:,.2f} ({v['percentage']:.1f}%) {v['type']} (Confidence: {v['confidence']:.1f}%)"
                for i, v in enumerate(top_variances[:5])])}

Please provide an executive summary with these sections:

1. EXECUTIVE OVERVIEW: Brief high-level summary (1 paragraph)
2. KEY FINDINGS: 3-5 bullet points of most important discoveries
3. FINANCIAL IMPACT: Analysis of total overspend/underspend and implications
4. ROOT CAUSE ANALYSIS: Common patterns and themes across investigations
5. RECOMMENDATIONS: Top 3 actionable recommendations with clear owners and timelines
6. RISK ASSESSMENT: Potential risks if issues are not addressed
7. NEXT STEPS: Clear action plan for immediate follow-up

Format: Professional business style. Use bullet points for clarity. Be specific and data-driven.
Provide COMPLETE sentences and thorough analysis."""

            logger.info(f"Generating executive summary for {total_variances} investigations...")
            summary = self.invoke(prompt, max_tokens=1500)
            
            # Clean up response
            summary = self._clean_response(summary)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = self.reports_dir / f"executive_summary_{timestamp}.txt"
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("EXECUTIVE SUMMARY - FP&A VARIANCE INVESTIGATION\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Investigations: {total_variances}\n")
                f.write(f"Investigations with Evidence: {variances_with_evidence}\n")
                f.write(f"Total Overspend: ${total_overspend:,.2f}\n")
                f.write(f"Total Underspend: ${total_underspend:,.2f}\n\n")
                f.write("SUMMARY:\n")
                f.write("-" * 70 + "\n")
                f.write(summary + "\n\n")
                
                # Add top variances
                f.write("TOP VARIANCES:\n")
                f.write("-" * 70 + "\n")
                for i, v in enumerate(top_variances[:5], 1):
                    f.write(f"{i}. {v['department']} - {v['account']}: ")
                    f.write(f"${v['amount']:,.2f} ({v['percentage']:.1f}%) {v['type']}\n")
            
            logger.info(f"✅ Saved executive summary to {summary_file}")
            
            return {
                "status": "SUCCESS",
                "summary": summary,
                "key_insights": self._extract_key_insights(summary),
                "recommendations": self._extract_recommendations(summary),
                "filepath": str(summary_file),
                "metrics": {
                    "total_variances": total_variances,
                    "variances_with_evidence": variances_with_evidence,
                    "total_overspend": total_overspend,
                    "total_underspend": total_underspend,
                    "generated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating executive summary: {e}")
            return {
                "status": "ERROR",
                "summary": f"Error generating summary: {str(e)}",
                "key_insights": [],
                "recommendations": [],
                "filepath": None
            }
    
    def generate_budget_adjustment_proposal(self, 
                                           variance_details: Dict,
                                           investigation_result: Dict,
                                           department: str) -> Dict[str, Any]:
        """Generate specific budget adjustment proposal with COMPLETE justification"""
        
        try:
            # Extract data with defaults
            account_name = variance_details.get('account_name', 'Unknown Account')
            account_code = variance_details.get('account_code', 'N/A')
            period = variance_details.get('period', 'Current Period')
            budget = float(variance_details.get('budget', 0))
            actual = float(variance_details.get('actual', 0))
            variance_amount = float(variance_details.get('variance_amount', 0))
            variance_percent = float(variance_details.get('variance_percentage', 0))
            
            # Get investigation data
            confidence = float(investigation_result.get('confidence', 0))
            evidence_count = int(investigation_result.get('evidence_count', 
                                                        investigation_result.get('evidence_found', 0)))
            root_cause = investigation_result.get('root_cause_analysis', '')
            analysis = investigation_result.get('analysis', '')
            
            # Calculate proposed budget adjustment
            abs_variance = abs(variance_amount)
            
            if variance_amount > 0:  # Overspend
                if abs_variance > settings.SIGNIFICANT_AMOUNT:
                    # Significant overspend: propose 80% adjustment
                    adjustment_type = "increase"
                    adjustment_amount = abs_variance * settings.BUDGET_ADJUSTMENT_OVERSEND_FACTOR
                    adjustment_reason = "significant overspend"
                else:
                    # Moderate overspend: propose full adjustment
                    adjustment_type = "increase"
                    adjustment_amount = abs_variance
                    adjustment_reason = "moderate overspend"
            else:  # Underspend
                if abs_variance > settings.SIGNIFICANT_AMOUNT:
                    # Significant underspend: propose 60% reduction
                    adjustment_type = "decrease"
                    adjustment_amount = abs_variance * settings.BUDGET_ADJUSTMENT_UNDERSPEND_FACTOR
                    adjustment_reason = "significant underspend"
                else:
                    # Moderate underspend: propose 50% reduction
                    adjustment_type = "decrease"
                    adjustment_amount = abs_variance * 0.5
                    adjustment_reason = "moderate underspend"
            
            # Ensure minimum proposal amount
            if adjustment_amount < settings.MIN_PROPOSAL_AMOUNT:
                adjustment_amount = settings.MIN_PROPOSAL_AMOUNT
            
            # Calculate proposed budget
            if adjustment_type == "increase":
                proposed_budget = budget + adjustment_amount
            else:
                proposed_budget = budget - adjustment_amount
            
            # Generate COMPLETE justification - FIXED VERSION
            justification = self._generate_detailed_justification_fixed(
                department=department,
                account_name=account_name,
                budget=budget,
                actual=actual,
                variance_amount=variance_amount,
                variance_percent=variance_percent,
                adjustment_type=adjustment_type,
                adjustment_amount=adjustment_amount,
                adjustment_reason=adjustment_reason,
                confidence=confidence,
                evidence_count=evidence_count,
                root_cause=root_cause,
                analysis=analysis,
                proposed_budget=proposed_budget
            )
            
            # Create proposal dict
            proposal = {
                "status": "SUCCESS",
                "department": department,
                "account": account_name,
                "account_code": account_code,
                "period": period,
                "current_budget": budget,
                "actual_spend": actual,
                "variance_amount": variance_amount,
                "variance_percentage": variance_percent,
                "proposed_budget": proposed_budget,
                "adjustment_amount": adjustment_amount,
                "adjustment_type": adjustment_type,
                "justification": justification,
                "investigation_confidence": confidence,
                "evidence_count": evidence_count,
                "root_cause_summary": root_cause[:200] + "..." if root_cause and len(root_cause) > 200 else root_cause,
                "generated_at": datetime.now().isoformat(),
                "approved": False,
                "approver": None,
                "approval_date": None
            }
            
            # Save proposal to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_account = account_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            safe_dept = department.replace(" ", "_")
            proposal_file = self.reports_dir / f"budget_proposal_{safe_dept}_{safe_account}_{timestamp}.json"
            
            with open(proposal_file, 'w', encoding='utf-8') as f:
                json.dump(proposal, f, indent=2, default=str)
            
            logger.info(f"✅ Saved budget proposal to {proposal_file}")
            
            # Also save as text file for easy reading
            text_file = proposal_file.with_suffix('.txt')
            self._save_proposal_as_text(proposal, text_file)
            
            proposal["filepath"] = str(proposal_file)
            proposal["text_filepath"] = str(text_file)
            
            return proposal
            
        except Exception as e:
            logger.error(f"❌ Error generating budget proposal: {e}")
            return {
                "status": "ERROR",
                "department": department,
                "account": variance_details.get('account_name', 'Unknown'),
                "adjustment_amount": 0.0,
                "adjustment_type": "none",
                "justification": f"Error generating proposal: {str(e)}",
                "current_budget": 0.0,
                "proposed_budget": 0.0,
                "filepath": None
            }
    
    def _generate_detailed_justification_fixed(self, department: str, account_name: str, budget: float,
                                             actual: float, variance_amount: float, variance_percent: float,
                                             adjustment_type: str, adjustment_amount: float, adjustment_reason: str,
                                             confidence: float, evidence_count: int, root_cause: str, analysis: str,
                                             proposed_budget: float) -> str:
        """Generate detailed, complete justification for budget proposal - FIXED VERSION"""
        
        # Build a simpler, more reliable prompt
        prompt = f"""Generate a detailed justification for a budget adjustment proposal.

PROPOSAL DETAILS:
- Department: {department}
- Account: {account_name}
- Current Budget: ${budget:,.2f}
- Actual Spend: ${actual:,.2f}
- Variance: ${variance_amount:,.2f} ({variance_percent:.1f}%)
- Proposed Adjustment: ${adjustment_amount:,.2f} ({adjustment_type})
- Proposed New Budget: ${proposed_budget:,.2f}
- Adjustment Reason: {adjustment_reason}
- Investigation Confidence: {confidence:.1f}%
- Supporting Documents: {evidence_count}

ROOT CAUSE SUMMARY:
{root_cause[:300] if root_cause else 'Based on investigation findings'}

ANALYSIS SUMMARY:
{analysis[:300] if analysis else 'General financial analysis'}

Create a professional justification that explains:
1. Why this adjustment is necessary
2. How it addresses the identified variance
3. What evidence supports this change
4. The business impact of making this adjustment
5. How it will prevent similar issues in the future

Provide a complete, well-structured justification suitable for management review.
Use complete sentences and be specific about the financial impact."""

        justification = self.invoke(prompt, max_tokens=600)
        
        # Clean and ensure complete sentences
        justification = self._clean_response(justification)
        justification = self._ensure_complete_sentences(justification)
        
        # If justification is still empty or too short, create a fallback
        if not justification or len(justification) < 50:
            if adjustment_type == "increase":
                justification = (f"This ${adjustment_amount:,.2f} budget increase is necessary because the {account_name} account in {department} "
                               f"experienced a ${abs(variance_amount):,.2f} overspend ({variance_percent:.1f}%). The adjustment aligns the budget "
                               f"with actual operational needs based on {evidence_count} supporting documents and {confidence:.1f}% investigation confidence.")
            else:
                justification = (f"This ${adjustment_amount:,.2f} budget decrease is appropriate because the {account_name} account in {department} "
                               f"showed a ${abs(variance_amount):,.2f} underspend ({abs(variance_percent):.1f}%). The adjustment optimizes budget allocation "
                               f"based on {evidence_count} supporting documents and {confidence:.1f}% investigation confidence.")
        
        return justification
    
    def _ensure_complete_sentences(self, text: str) -> str:
        """Ensure text ends with complete sentences"""
        if not text:
            return text
        
        # Remove trailing ellipses or incomplete thoughts
        text = text.rstrip('.… ')
        
        # Ensure it ends with proper punctuation
        if text and text[-1] not in ['.', '!', '?']:
            # Find the last complete sentence
            sentences = [s.strip() for s in text.split('. ') if s.strip()]
            if sentences:
                text = '. '.join(sentences) + '.'
            else:
                text = text + '.'
        
        return text
    
    def _save_proposal_as_text(self, proposal: Dict, filepath: Path):
        """Save proposal as human-readable text file"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("BUDGET ADJUSTMENT PROPOSAL\n")
                f.write("=" * 70 + "\n\n")
                
                f.write(f"PROPOSAL ID: {filepath.stem}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Status: {proposal.get('status', 'DRAFT')}\n\n")
                
                f.write("1. BASIC INFORMATION:\n")
                f.write("-" * 70 + "\n")
                f.write(f"Department: {proposal['department']}\n")
                f.write(f"Account: {proposal['account']} ({proposal['account_code']})\n")
                f.write(f"Period: {proposal['period']}\n")
                f.write(f"Investigation Confidence: {proposal['investigation_confidence']:.1f}%\n")
                f.write(f"Evidence Documents: {proposal['evidence_count']}\n\n")
                
                f.write("2. FINANCIAL DETAILS:\n")
                f.write("-" * 70 + "\n")
                f.write(f"Current Budget:      ${proposal['current_budget']:,.2f}\n")
                f.write(f"Actual Spend:        ${proposal['actual_spend']:,.2f}\n")
                f.write(f"Variance Amount:     ${proposal['variance_amount']:,.2f}\n")
                f.write(f"Variance Percentage: {proposal['variance_percentage']:.1f}%\n")
                f.write(f"Proposed Adjustment: ${proposal['adjustment_amount']:,.2f} ({proposal['adjustment_type']})\n")
                f.write(f"Proposed New Budget: ${proposal['proposed_budget']:,.2f}\n\n")
                
                f.write("3. JUSTIFICATION:\n")
                f.write("-" * 70 + "\n")
                f.write(f"{proposal['justification']}\n\n")
                
                if 'root_cause_summary' in proposal and proposal['root_cause_summary']:
                    f.write("4. ROOT CAUSE SUMMARY:\n")
                    f.write("-" * 70 + "\n")
                    f.write(f"{proposal['root_cause_summary']}\n\n")
                
                f.write("5. APPROVAL STATUS:\n")
                f.write("-" * 70 + "\n")
                f.write(f"Approved: {proposal.get('approved', False)}\n")
                if proposal.get('approver'):
                    f.write(f"Approver: {proposal['approver']}\n")
                if proposal.get('approval_date'):
                    f.write(f"Approval Date: {proposal['approval_date']}\n")
                
                f.write("\n" + "=" * 70 + "\n")
                f.write("END OF PROPOSAL\n")
                f.write("=" * 70 + "\n")
            
            logger.debug(f"Saved text version to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving proposal text: {e}")
    
    def generate_detailed_report(self, investigation_result: Dict) -> Dict[str, Any]:
        """Generate detailed investigation report"""
        
        try:
            variance = investigation_result.get("variance_details", {})
            department = investigation_result.get('department', 'Unknown')
            account_name = variance.get('account_name', 'Unknown Account')
            evidence_count = investigation_result.get('evidence_found', 0)
            investigation_data = investigation_result.get("investigation_result", {})
            
            prompt = f"""Generate a detailed investigation report for internal documentation.

REPORT DETAILS:
- Department: {department}
- Account: {account_name} ({variance.get('account_code', 'N/A')})
- Period: {variance.get('period', 'Unknown')}
- Budget vs Actual: ${variance.get('budget', 0):,.2f} vs ${variance.get('actual', 0):,.2f}
- Variance Amount: ${variance.get('variance_amount', 0):,.2f} ({variance.get('variance_percentage', 0):.1f}%)
- Evidence Collected: {evidence_count} documents
- Investigation Confidence: {investigation_data.get('confidence', 0):.1f}%

EVIDENCE SUMMARY:
{investigation_result.get('evidence_summary', 'No summary available')}

INVESTIGATION ANALYSIS:
{investigation_data.get('analysis', 'No analysis available')}

ROOT CAUSE ANALYSIS:
{investigation_data.get('root_cause_analysis', 'No root cause analysis available')}

RECOMMENDATIONS:
{chr(10).join(['- ' + rec for rec in investigation_data.get('recommendations', ['No recommendations'])])}

Create a comprehensive investigation report with these sections:

1. EXECUTIVE SUMMARY (Brief overview of findings)
2. INVESTIGATION SCOPE & METHODOLOGY (How the investigation was conducted)
3. FINANCIAL DATA ANALYSIS (Detailed analysis of budget vs actual)
4. EVIDENCE REVIEW & DOCUMENTATION (Summary of supporting documents)
5. ROOT CAUSE IDENTIFICATION (Detailed root cause analysis with evidence)
6. IMPACT ASSESSMENT (Financial, Operational, Compliance impacts)
7. FINDINGS & CONCLUSIONS (Key findings from the investigation)
8. RECOMMENDATIONS (Immediate, Short-term, Long-term actions)
9. LESSONS LEARNED & PROCESS IMPROVEMENTS
10. APPENDIX: Evidence log and references

Format professionally for audit and compliance purposes with complete sentences and thorough analysis."""

            logger.info(f"Generating detailed report for {department} - {account_name}...")
            report = self.invoke(prompt, max_tokens=2000)
            
            # Clean up response
            report = self._clean_response(report)
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_account = account_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            safe_dept = department.replace(" ", "_")
            report_file = self.reports_dir / f"detailed_report_{safe_dept}_{safe_account}_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("DETAILED INVESTIGATION REPORT\n")
                f.write("=" * 70 + "\n\n")
                
                f.write(f"Report ID: {report_file.stem}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Department: {department}\n")
                f.write(f"Account: {account_name}\n")
                f.write(f"Evidence Analyzed: {evidence_count} documents\n")
                f.write(f"Investigation Confidence: {investigation_data.get('confidence', 0):.1f}%\n\n")
                
                f.write("REPORT CONTENTS:\n")
                f.write("-" * 70 + "\n")
                f.write(report + "\n\n")
                
                # Add metadata
                f.write("INVESTIGATION METADATA:\n")
                f.write("-" * 70 + "\n")
                f.write(f"Budget: ${variance.get('budget', 0):,.2f}\n")
                f.write(f"Actual: ${variance.get('actual', 0):,.2f}\n")
                f.write(f"Variance: ${variance.get('variance_amount', 0):,.2f}\n")
                f.write(f"Percentage: {variance.get('variance_percentage', 0):.1f}%\n")
                f.write(f"Evidence Summary: {investigation_result.get('evidence_summary', 'N/A')}\n")
                f.write(f"Root Cause Summary: {investigation_data.get('root_cause_analysis', 'N/A')[:200]}\n")
            
            logger.info(f"✅ Saved detailed report to {report_file}")
            
            return {
                "status": "SUCCESS",
                "report": report,
                "filepath": str(report_file),
                "sections": self._extract_report_sections(report),
                "department": department,
                "account": account_name,
                "evidence_count": evidence_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating detailed report: {e}")
            return {
                "status": "ERROR",
                "report": f"Error generating report: {str(e)}",
                "filepath": None,
                "sections": []
            }
    
    def _clean_response(self, response: str) -> str:
        """Clean LLM response by removing thinking tags and incomplete sentences"""
        if not response:
            return response
            
        # Remove <think>...</think> blocks
        import re
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove standalone <think> tags
        response = response.replace('<think>', '').replace('</think>', '')
        
        # Remove thinking patterns
        response = re.sub(r'(?i)thought process.*?:', '', response)
        response = re.sub(r'(?i)let me think.*?\.', '', response)
        response = re.sub(r'(?i)first,.*?\.', '', response)
        response = re.sub(r'(?i)alright,.*?\.', '', response)
        response = re.sub(r'(?i)okay,.*?\.', '', response)
        
        # Remove multiple newlines
        response = re.sub(r'\n\s*\n', '\n\n', response)
        
        # Remove trailing incomplete sentences
        lines = response.strip().split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and not line.endswith('...'):
                cleaned_lines.append(line)
        
        response = '\n'.join(cleaned_lines)
        
        # Ensure the response ends with proper punctuation
        if response and response[-1] not in ['.', '!', '?', ')', ']', '}']:
            # Find last complete sentence
            sentences = re.split(r'(?<=[.!?])\s+', response)
            if sentences and len(sentences) > 1:
                response = ' '.join(sentences[:-1])
            elif sentences:
                response = sentences[0]
                
        return response.strip()
    
    def _extract_key_insights(self, summary: str) -> List[str]:
        """Extract key insights from summary"""
        insights = []
        lines = summary.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 20:
                lower_line = line.lower()
                if any(indicator in lower_line for indicator in ['insight:', 'finding:', 'key:', 'discovery:', '- ', '• ', '* ']):
                    insights.append(line)
                elif line.startswith(('The analysis reveals', 'Key findings include', 'Investigation shows', 'Primary insight')):
                    insights.append(line)
        
        return insights[:5] if insights else ["Review detailed reports for specific insights."]
    
    def _extract_recommendations(self, summary: str) -> List[str]:
        """Extract recommendations from summary"""
        recommendations = []
        lines = summary.split('\n')
        
        in_recommendations = False
        for line in lines:
            line = line.strip()
            lower_line = line.lower()
            
            if 'recommendation' in lower_line or 'next step' in lower_line or 'action:' in lower_line:
                in_recommendations = True
            
            if in_recommendations and line:
                if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
                    recommendations.append(line)
                elif len(recommendations) > 0 and not line.startswith(('6.', '7.', '8.', '9.')):
                    # Append to last recommendation if continuation
                    recommendations[-1] += " " + line
        
        return recommendations[:5] if recommendations else ["Review full investigation reports for specific recommendations."]
    
    def _extract_report_sections(self, report: str) -> Dict[str, str]:
        """Extract report sections"""
        sections = {}
        current_section = "Introduction"
        current_content = []
        
        lines = report.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check for section headers
            if (len(line_stripped) > 3 and 
                (line_stripped.upper() == line_stripped or 
                 line_stripped.startswith(tuple([f'{i}.' for i in range(1, 20)]))) and 
                len(line_stripped.split()) < 15):
                
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line_stripped
                current_content = []
            elif line_stripped:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections