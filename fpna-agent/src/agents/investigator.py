# src/agents/investigator.py
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from src.rag.retriever import RAGRetriever
import logging

logger = logging.getLogger(__name__)

class InvestigatorAgent(BaseAgent):
    """Agent for investigating financial variances"""
    
    def __init__(self, rag_retriever: RAGRetriever):
        system_prompt = """You are a Financial Investigator Agent specialized in analyzing budget variances.
        
        Your role is to:
        1. Investigate the root causes of financial variances
        2. Analyze supporting documents and evidence
        3. Identify patterns and trends in spending
        4. Provide actionable insights for remediation
        5. Assess confidence levels based on evidence
        
        BE SPECIFIC AND DETAILED:
        - Provide comprehensive root cause analysis
        - Give specific examples from evidence
        - Explain the business impact
        - Suggest concrete next steps
        
        IMPORTANT: Always provide complete, final answers without any thinking process or <think> tags.
        Provide specific analysis and clear recommendations with full sentences."""
        
        super().__init__("InvestigatorAgent", system_prompt)
        self.rag_retriever = rag_retriever
    
    def investigate_variance(self, variance_details: Dict, department: str = None) -> Dict[str, Any]:
        """Investigate a specific variance"""
        try:
            # Extract variance information
            account_name = variance_details.get('account_name', 'Unknown Account')
            variance_amount = variance_details.get('variance_amount', 0)
            variance_percent = variance_details.get('variance_percentage', 0)
            budget = variance_details.get('budget', 0)
            actual = variance_details.get('actual', 0)
            period = variance_details.get('period', 'Current Period')
            
            # Get department from variance or parameter
            dept = department or variance_details.get('department', 'Unknown')
            
            logger.info(f"Investigating variance: {account_name} in {dept}")
            
            # Search for relevant documents
            search_queries = [
                f"{dept} {account_name} variance",
                f"{account_name} budget actual difference",
                f"{dept} spending {account_name} documents",
                f"{account_name} invoice contract agreement"
            ]
            
            all_documents = []
            for query in search_queries[:2]:  # Limit to 2 queries for speed
                try:
                    results = self.rag_retriever.retrieve_relevant_documents(query)
                    if results.get('organized_documents'):
                        for docs in results['organized_documents'].values():
                            all_documents.extend(docs)
                except Exception as e:
                    logger.warning(f"Search query failed: {query}, error: {e}")
                    continue
            
            # Count evidence
            evidence_count = len(all_documents)
            evidence_summary = self._summarize_evidence(all_documents)
            
            # Get document content for analysis
            document_content = self._extract_document_content(all_documents)
            
            # Analyze the variance
            analysis = self._analyze_variance(variance_details, evidence_summary, document_content, dept)
            
            # Determine root cause
            root_cause = self._determine_root_cause(variance_details, analysis, evidence_summary, document_content)
            
            # Calculate confidence
            confidence = self._calculate_confidence(evidence_count, analysis, root_cause)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(variance_details, root_cause, dept, document_content)
            
            return {
                "status": "SUCCESS",
                "department": dept,
                "account": account_name,
                "period": period,
                "variance_amount": variance_amount,
                "variance_percentage": variance_percent,
                "evidence_found": evidence_count,
                "evidence_summary": evidence_summary,
                "investigation_result": {
                    "analysis": analysis,
                    "root_cause_analysis": root_cause,
                    "confidence": confidence,
                    "recommendations": recommendations,
                    "document_references": self._extract_document_references(all_documents)
                }
            }
            
        except Exception as e:
            logger.error(f"Error investigating variance: {e}")
            return {
                "status": "ERROR",
                "department": department or variance_details.get('department', 'Unknown'),
                "account": variance_details.get('account_name', 'Unknown'),
                "error": str(e),
                "evidence_found": 0,
                "evidence_summary": "Investigation failed",
                "investigation_result": {
                    "analysis": f"Investigation failed: {str(e)}",
                    "root_cause_analysis": "Unable to determine due to investigation error",
                    "confidence": 0,
                    "recommendations": ["Review variance manually due to investigation error"]
                }
            }
    
    def _summarize_evidence(self, documents: List) -> str:
        """Summarize the evidence found"""
        if not documents:
            return "No relevant documents found"
        
        # Get unique document sources with brief content
        sources_info = []
        for doc in documents[:5]:  # Limit to 5 documents for summary
            source = doc.metadata.get('source', 'Unknown')
            content_preview = doc.page_content[:100] if len(doc.page_content) > 100 else doc.page_content
            
            if source:
                filename = source.split('/')[-1] if '/' in source else source
                sources_info.append(f"{filename}: {content_preview}...")
        
        if sources_info:
            return f"Found {len(documents)} documents. Key documents: " + "; ".join(sources_info)
        else:
            return f"Found {len(documents)} relevant documents"
    
    def _extract_document_content(self, documents: List) -> str:
        """Extract relevant document content for analysis"""
        if not documents:
            return "No document content available"
        
        content_parts = []
        for i, doc in enumerate(documents[:3]):  # Limit to 3 documents
            source = doc.metadata.get('source', f'Document {i+1}')
            content = doc.page_content[:300]  # Limit content length
            content_parts.append(f"[{source}]: {content}")
        
        return "\n\n".join(content_parts)
    
    def _extract_document_references(self, documents: List) -> List[str]:
        """Extract document references for citations"""
        references = []
        for doc in documents[:5]:  # Limit to 5 references
            source = doc.metadata.get('source', 'Unknown Document')
            references.append(source)
        return references
    
    def _analyze_variance(self, variance_details: Dict, evidence_summary: str, document_content: str, department: str) -> str:
        """Analyze the variance with evidence"""
        account_name = variance_details.get('account_name', 'Unknown')
        variance_amount = variance_details.get('variance_amount', 0)
        variance_percent = variance_details.get('variance_percentage', 0)
        budget = variance_details.get('budget', 0)
        actual = variance_details.get('actual', 0)
        
        prompt = f"""Comprehensively analyze this financial variance:

FINANCIAL DETAILS:
- Department: {department}
- Account: {account_name}
- Period: {variance_details.get('period', 'Current Period')}
- Budget: ${budget:,.2f}
- Actual: ${actual:,.2f}
- Variance: ${variance_amount:,.2f} ({variance_percent:.1f}%)
- Variance Type: {'OVERSPEND' if variance_amount > 0 else 'UNDERSPEND'}

EVIDENCE SUMMARY:
{evidence_summary}

DOCUMENT CONTENT (for reference):
{document_content}

Please provide a detailed analysis covering:
1. CONTEXTUAL ANALYSIS: Business context of this expense category
2. QUANTITATIVE ASSESSMENT: Magnitude and significance of variance
3. EVIDENCE CORRELATION: How documents explain or relate to the variance
4. TEMPORAL PATTERNS: Is this a one-time event or recurring pattern?
5. BUSINESS IMPACT: Operational and financial implications
6. PRELIMINARY FINDINGS: Initial observations based on evidence

Provide a comprehensive analysis (4-6 paragraphs)."""

        return self.invoke(prompt, max_tokens=800)
    
    def _determine_root_cause(self, variance_details: Dict, analysis: str, evidence_summary: str, document_content: str) -> str:
        """Determine the root cause of the variance"""
        account_name = variance_details.get('account_name', 'Unknown')
        variance_amount = variance_details.get('variance_amount', 0)
        variance_percent = variance_details.get('variance_percentage', 0)
        
        prompt = f"""Based on the analysis and evidence, determine the SPECIFIC ROOT CAUSE(S):

ACCOUNT: {account_name}
VARIANCE: ${variance_amount:,.2f} ({variance_percent:.1f}%)

ANALYSIS SUMMARY:
{analysis[:500]}...

EVIDENCE:
{evidence_summary}

DOCUMENT CONTENT:
{document_content[:300]}...

Identify SPECIFIC root causes by considering:

POSSIBLE CAUSES:
1. BUDGETING ISSUES: Initial budget was inaccurate, market changes, new requirements
2. OPERATIONAL FACTORS: Process changes, new initiatives, scaling, efficiency changes
3. PROCUREMENT/CONTRACT ISSUES: Vendor changes, contract terms, pricing adjustments
4. TIMING DIFFERENCES: Accrual vs cash, project phasing, seasonal factors
5. CONTROL ISSUES: Approval gaps, policy compliance, documentation issues
6. EXTERNAL FACTORS: Market conditions, regulatory changes, economic factors
7. ONE-TIME EVENTS: Special projects, emergencies, capital investments

Provide SPECIFIC root cause analysis with:
- Primary root cause (most likely)
- Supporting evidence from documents
- Contributing factors
- Business process implications

Format: Clear, specific, evidence-based (3-4 paragraphs)."""

        return self.invoke(prompt, max_tokens=600)
    
    def _calculate_confidence(self, evidence_count: int, analysis: str, root_cause: str) -> float:
        """Calculate confidence level based on evidence and analysis"""
        # Base confidence on evidence
        if evidence_count >= 5:
            base_confidence = 85.0
        elif evidence_count >= 2:
            base_confidence = 70.0
        elif evidence_count >= 1:
            base_confidence = 55.0
        else:
            base_confidence = 35.0
        
        # Adjust based on analysis quality
        if "specific" in analysis.lower() and "evidence" in analysis.lower():
            base_confidence += 15.0
        if "detailed" in analysis.lower() or "comprehensive" in analysis.lower():
            base_confidence += 10.0
        
        # Adjust based on root cause specificity
        if "unclear" in root_cause.lower() or "insufficient" in root_cause.lower():
            base_confidence -= 20.0
        elif "specific" in root_cause.lower() or "identified" in root_cause.lower():
            base_confidence += 10.0
        
        # Cap between 0 and 100
        return max(0.0, min(100.0, base_confidence))
    
    def _generate_recommendations(self, variance_details: Dict, root_cause: str, department: str, document_content: str) -> List[str]:
        """Generate recommendations based on variance and root cause"""
        account_name = variance_details.get('account_name', 'Unknown')
        variance_amount = variance_details.get('variance_amount', 0)
        variance_percent = variance_details.get('variance_percentage', 0)
        
        prompt = f"""Generate SPECIFIC, ACTIONABLE recommendations:

CONTEXT:
- Department: {department}
- Account: {account_name}
- Variance: ${variance_amount:,.2f} ({variance_percent:.1f}%)
- Variance Type: {'Overspend' if variance_amount > 0 else 'Underspend'}

ROOT CAUSE ANALYSIS:
{root_cause[:300]}...

DOCUMENT CONTEXT:
{document_content[:200]}...

Generate 3 SPECIFIC recommendations that:
1. DIRECTLY ADDRESS the identified root cause
2. Are CONCRETE and IMPLEMENTABLE
3. Have CLEAR OWNERSHIP (specify role/department)
4. Include MEASURABLE OUTCOMES
5. Consider BUSINESS IMPACT

For each recommendation, specify:
- ACTION: What needs to be done
- OWNER: Who is responsible
- TIMELINE: When it should be completed
- OUTCOME: Expected result

Format each recommendation clearly and separately."""

        response = self.invoke(prompt, max_tokens=500)
        
        # Extract recommendations
        recommendations = []
        current_rec = ""
        
        for line in response.split('\n'):
            line = line.strip()
            if line and len(line) > 10:
                # Check for recommendation indicators
                if line.lower().startswith(('recommendation', 'action', '1.', '2.', '3.', '-', '•', '*', 'a.', 'b.', 'c.')):
                    if current_rec:
                        recommendations.append(current_rec.strip())
                    current_rec = line
                elif current_rec:
                    current_rec += " " + line
        
        # Add last recommendation
        if current_rec:
            recommendations.append(current_rec.strip())
        
        # Ensure we have at least 2 recommendations
        if len(recommendations) < 2:
            if variance_amount > 0:
                recommendations.append(f"Review and adjust {account_name} budget allocation in {department} based on actual spending patterns")
                recommendations.append(f"Implement spending controls and approval processes for {account_name} in {department}")
            else:
                recommendations.append(f"Analyze {account_name} underspend in {department} for potential budget reallocation")
                recommendations.append(f"Review procurement processes for {account_name} in {department} to optimize spending")
        
        return recommendations[:3]