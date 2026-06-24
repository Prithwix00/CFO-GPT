#!/usr/bin/env python3
"""
Main entry point for the FP&A Agent System
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import settings
from src.utils.data_loader import DataLoader, FinancialData
from src.agents.monitor_agent import MonitorAgent
from src.agents.investigator import InvestigatorAgent
from src.agents.reporter_agent import ReporterAgent
from src.rag.loader import DocumentLoader
from src.rag.vector_store import VectorStore
from src.rag.retriever import RAGRetriever
from src.workflows.fpa_workflow import FPAWorkflow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FPASystem:
    """Main FP&A System orchestrator"""
    
    def __init__(self):
        logger.info("Initializing FP&A System...")
        
        # Ensure report directory exists
        reports_dir = Path(settings.REPORTS_DIR)
        reports_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"Report directory: {reports_dir}")
        
        # Initialize components
        self.data_loader = DataLoader(settings.DATA_DIR)
        self.document_loader = DocumentLoader(settings.UPLOAD_DIR)
        
        # Initialize agents
        self.monitor_agent = MonitorAgent()
        
        # Initialize RAG system
        self.vector_store = VectorStore()
        self.rag_retriever = RAGRetriever(self.vector_store, self.monitor_agent)
        self.investigator_agent = InvestigatorAgent(self.rag_retriever)
        self.reporter_agent = ReporterAgent()
        
        # Initialize workflow
        self.workflow = FPAWorkflow(
            monitor_agent=self.monitor_agent,
            investigator_agent=self.investigator_agent,
            reporter_agent=self.reporter_agent,
            rag_retriever=self.rag_retriever
        )
        
        logger.info("FP&A System initialized successfully")
    
    def load_sample_data(self) -> list[FinancialData]:
        """Load or generate sample financial data"""
        sample_file = os.path.join(settings.DATA_DIR, "sample_financial_data.json")
        
        if os.path.exists(sample_file):
            logger.info(f"Loading sample data from {sample_file}")
            return self.data_loader.load_json_data(sample_file)
        else:
            logger.info("Generating sample financial data")
            sample_data = self.data_loader.generate_sample_data()
            self.data_loader.save_financial_data(sample_data, "sample_financial_data.json")
            return sample_data
    
    def load_documents(self, directory: str = None) -> list:
        """Load documents for RAG system"""
        if directory is None:
            directory = settings.UPLOAD_DIR
        
        logger.info(f"Loading documents from {directory}")
        
        if not os.path.exists(directory):
            logger.warning(f"Document directory {directory} does not exist")
            return []
        
        documents = self.document_loader.load_directory(directory)
        
        if documents:
            # Add to vector store
            self.vector_store.add_documents(documents)
            logger.info(f"Loaded {len(documents)} documents into vector store")
        
        return documents
    
    def run_complete_analysis(self, department: str = None):
        """Run complete FP&A analysis workflow"""
        logger.info("Starting complete FP&A analysis")
        
        # Step 1: Load financial data
        financial_data = self.load_sample_data()
        logger.info(f"Loaded {len(financial_data)} financial records")
        
        # Step 2: Load documents
        documents = self.load_documents()
        logger.info(f"Loaded {len(documents)} supporting documents")
        
        # Step 3: Run workflow
        results = self.workflow.run(
            financial_data=financial_data,
            documents=documents,
            department_filter=department
        )
        
        # Step 4: Display results
        self._display_results(results)
        
        return results
    
    def _display_results(self, results: dict):
        """Display analysis results with detailed information"""
        print("\n" + "="*80)
        print("📊 FP&A ANALYSIS RESULTS")
        print("="*80)
        
        if results["status"] == "failed":
            print(f"\n❌ Analysis failed: {results.get('error')}")
            return
        
        metrics = results["metrics"]
        print(f"\n📈 METRICS:")
        print(f"   • Total variances analyzed: {metrics['total_variances_analyzed']}")
        print(f"   • Significant variances found: {metrics['significant_variances_found']}")
        print(f"   • Investigations completed: {metrics['investigations_completed']}")
        print(f"   • Budget proposals generated: {metrics['proposals_generated']}")
        print(f"   • Recommendations generated: {metrics.get('recommendations_generated', 0)}")
        print(f"   • Processing time: {metrics['processing_time']}")
        
        # Show detailed variances
        variance_analysis = results.get("results", {}).get("variance_analysis", {})
        if variance_analysis and variance_analysis.get("significant_variances"):
            print(f"\n🔍 SIGNIFICANT VARIANCES DETAILS:")
            print("-"*80)
            sig_vars = variance_analysis["significant_variances"]
            for i, var in enumerate(sig_vars[:5], 1):
                print(f"\n{i}. {var.get('department', 'Unknown')} - {var.get('account_name', 'Unknown')}")
                print(f"   • Budget:    ${var.get('budget', 0):,.2f}")
                print(f"   • Actual:    ${var.get('actual', 0):,.2f}")
                print(f"   • Variance:  ${var.get('variance_amount', 0):,.2f} ({var.get('variance_percentage', 0):.1f}%)")
                print(f"   • Reason:    {var.get('reason', 'No reason provided')}")
        
        # Show investigation findings with ROOT CAUSES
        investigation_results = results.get("results", {}).get("investigation_results", [])
        if investigation_results:
            print(f"\n🔎 INVESTIGATION FINDINGS (with Root Cause Analysis):")
            print("-"*80)
            successful_investigations = [inv for inv in investigation_results if inv.get('status') == 'SUCCESS']
            
            for i, inv in enumerate(successful_investigations[:3], 1):
                variance = inv.get('variance_details', {})
                department = inv.get('department', 'Unknown')
                account = variance.get('account_name', 'Unknown')
                investigation_data = inv.get('investigation_result', {})
                
                print(f"\n{i}. {department} - {account}")
                print(f"   • Evidence Found: {inv.get('evidence_found', 0)} documents")
                
                # Show evidence summary
                evidence_summary = inv.get('evidence_summary', '')
                if evidence_summary and evidence_summary != 'No relevant documents found':
                    if len(evidence_summary) > 100:
                        evidence_summary = evidence_summary[:100] + "..."
                    print(f"   • Evidence: {evidence_summary}")
                
                # Show confidence
                confidence = investigation_data.get('confidence', 0)
                if confidence > 0:
                    print(f"   • Confidence: {confidence:.1f}%")
                
                # Show ROOT CAUSE ANALYSIS - Complete display
                root_cause = investigation_data.get('root_cause_analysis', '')
                if root_cause and len(root_cause) > 50 and "insufficient evidence" not in root_cause.lower():
                    print(f"   • Root Cause Analysis:")
                    
                    # Clean and format root cause for display
                    root_cause = root_cause.replace('<think>', '').replace('</think>', '').strip()
                    
                    # Split into sentences and display first 3-4 meaningful ones
                    sentences = [s.strip() for s in root_cause.split('.') if s.strip()]
                    meaningful_sentences = [s for s in sentences if len(s) > 20]
                    
                    for j, sentence in enumerate(meaningful_sentences[:3]):
                        if sentence:
                            print(f"      {j+1}. {sentence}.")
                    
                    if len(meaningful_sentences) > 3:
                        print(f"      ... [see detailed report for complete analysis]")
                
                # Show key recommendation if available
                recommendations = investigation_data.get('recommendations', [])
                if recommendations and len(recommendations) > 0:
                    # Clean recommendation
                    rec = recommendations[0].replace('<think>', '').replace('</think>', '').strip()
                    if len(rec) > 120:
                        rec = rec[:120] + "..."
                    print(f"   • Key Recommendation: {rec}")
        
        # Show recommendations - IMPROVED VERSION
        recommendations = results.get("results", {}).get("recommendations", [])
        if recommendations:
            print(f"\n✅ ACTIONABLE RECOMMENDATIONS ({len(recommendations)}):")
            print("-"*80)
            for i, rec in enumerate(recommendations[:10], 1):
                if isinstance(rec, dict):
                    action = rec.get('action', 'No action specified')
                    priority = rec.get('priority', 'MEDIUM')
                    department = rec.get('department', 'Unknown')
                    account = rec.get('account', 'Unknown')
                    
                    print(f"\n{i}. [{priority}] {action}")
                    print(f"   Department: {department}")
                    print(f"   Account: {account}")
                    
                    # Show variance amount
                    if rec.get('variance_amount'):
                        amount = rec['variance_amount']
                        sign = "+" if amount > 0 else ""
                        print(f"   Variance: {sign}${abs(amount):,.2f}")
                    
                    if rec.get('owner'):
                        print(f"   Owner: {rec['owner']}")
                    if rec.get('timeline'):
                        print(f"   Timeline: {rec['timeline']}")
                    if rec.get('impact'):
                        print(f"   Impact: {rec['impact']}")
                    if rec.get('details'):
                        details = rec['details']
                        details = details.replace('<think>', '').replace('</think>', '').strip()
                        if len(details) > 150:
                            details = details[:150] + "..."
                        print(f"   Details: {details}")
                else:
                    # Clean text recommendation
                    rec_text = str(rec).replace('<think>', '').replace('</think>', '').strip()
                    print(f"{i}. {rec_text}")
        
        # Show budget proposals - FIXED VERSION with proper justification handling
        budget_proposals = results.get("results", {}).get("budget_proposals", [])
        if budget_proposals:
            print(f"\n💰 BUDGET PROPOSALS ({len(budget_proposals)}):")
            print("-"*80)
            for i, prop in enumerate(budget_proposals, 1):
                if isinstance(prop, dict):
                    status = prop.get('status', 'UNKNOWN')
                    if status == 'SUCCESS':
                        dept = prop.get('department', 'Unknown')
                        account = prop.get('account', 'Unknown')
                        adj_type = prop.get('adjustment_type', 'adjustment')
                        
                        # Format amounts
                        current = float(prop.get('current_budget', 0))
                        proposed = float(prop.get('proposed_budget', 0))
                        amount = float(prop.get('adjustment_amount', 0))
                        variance = float(prop.get('variance_amount', 0))
                        actual_spend = prop.get('actual_spend', current + variance)
                        
                        print(f"\n{i}. {dept} - {account}")
                        print(f"   • Current Budget:    ${current:,.2f}")
                        print(f"   • Actual Spend:      ${actual_spend:,.2f}")
                        print(f"   • Variance:          ${variance:,.2f} ({prop.get('variance_percentage', 0):.1f}%)")
                        print(f"   • Proposed Budget:   ${proposed:,.2f}")
                        print(f"   • Adjustment:        ${amount:,.2f} ({adj_type})")
                        
                        # Show justification - FIXED: Properly handles empty justifications
                        justification = prop.get('justification', '')
                        if justification and justification.strip():
                            # Clean any thinking tags
                            justification = justification.replace('<think>', '').replace('</think>', '').strip()
                            
                            # Split into reasonable chunks for display
                            sentences = [s.strip() for s in justification.split('. ') if s.strip()]
                            
                            if sentences:
                                print(f"   • Justification:")
                                # Show first 3 sentences
                                for j, sentence in enumerate(sentences[:3]):
                                    if sentence and not sentence.endswith('.'):
                                        sentence = sentence + '.'
                                    print(f"      {j+1}. {sentence}")
                                
                                if len(sentences) > 3:
                                    print(f"      ... [see proposal file for complete justification]")
                            else:
                                # Fallback if no sentences found
                                if variance > 0:
                                    print(f"   • Justification: Budget increase required to address ${abs(variance):,.2f} overspend in {account}")
                                else:
                                    print(f"   • Justification: Budget decrease based on ${abs(variance):,.2f} underspend in {account}")
                        else:
                            # Generate a simple justification if empty
                            if variance > 0:
                                print(f"   • Justification: Budget increase required to address ${abs(variance):,.2f} overspend in {account}")
                            else:
                                print(f"   • Justification: Budget decrease based on ${abs(variance):,.2f} underspend in {account}")
                        
                        # Show investigation confidence
                        confidence = prop.get('investigation_confidence', 0)
                        if confidence > 0:
                            print(f"   • Confidence Level:  {confidence:.1f}%")
                        
                        # Show evidence count
                        evidence_count = prop.get('evidence_count', 0)
                        if evidence_count > 0:
                            print(f"   • Evidence:          {evidence_count} supporting documents")
                        
                        # Show file if saved
                        if 'filepath' in prop:
                            filename = Path(prop['filepath']).name
                            print(f"   • Saved as:          {filename}")
                    else:
                        error_msg = prop.get('justification', prop.get('error', 'Unknown error'))
                        error_msg = error_msg.replace('<think>', '').replace('</think>', '').strip()
                        print(f"\n{i}. ⚠️ Proposal Failed: {error_msg}")
        
        # Show executive summary if available
        executive_summary = results.get("results", {}).get("executive_summary", {})
        if executive_summary and executive_summary.get('status') == 'SUCCESS':
            print(f"\n📋 EXECUTIVE SUMMARY:")
            print("-"*80)
            summary = executive_summary.get('summary', '')
            if summary:
                # Clean thinking tags
                summary = summary.replace('<think>', '').replace('</think>', '').strip()
                
                if len(summary) > 400:
                    # Show first paragraph or 400 chars
                    paragraphs = summary.split('\n\n')
                    if paragraphs:
                        print(paragraphs[0])
                        if len(paragraphs) > 1:
                            print("\n[Summary continues in saved file...]")
                    else:
                        # Try splitting by sentences
                        sentences = [s.strip() for s in summary.split('. ') if s.strip()]
                        if sentences:
                            displayed = '. '.join(sentences[:3]) + '.'
                            print(f"{displayed}")
                            if len(sentences) > 3:
                                print(f"\n[Summary continues in saved file...]")
                        else:
                            print(f"{summary[:400]}...")
                    print(f"\n[Full summary saved to: {executive_summary.get('filepath', 'Unknown')}]")
                else:
                    print(summary)
        
        # Show report file locations
        print(f"\n📁 REPORT FILES SAVED TO:")
        print("-"*80)
        reports_dir = Path(settings.REPORTS_DIR)
        if reports_dir.exists():
            files = list(reports_dir.glob("*"))
            if files:
                # Sort by modification time (newest first)
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for f in files[:5]:  # Show first 5 files
                    size_kb = f.stat().st_size / 1024
                    mod_time = datetime.fromtimestamp(f.stat().st_mtime).strftime('%H:%M')
                    
                    # Add emoji based on file type
                    if f.suffix == '.json':
                        file_emoji = "📊"
                    elif f.suffix == '.txt':
                        file_emoji = "📄"
                    else:
                        file_emoji = "📁"
                    
                    print(f"  {file_emoji} {f.name} ({size_kb:.1f} KB, {mod_time})")
                if len(files) > 5:
                    print(f"  • ... and {len(files) - 5} more files")
                    
                # Show statistics
                json_files = len([f for f in files if f.suffix == '.json'])
                txt_files = len([f for f in files if f.suffix == '.txt'])
                other_files = len(files) - json_files - txt_files
                print(f"\n  📊 Statistics: {json_files} JSON files, {txt_files} text files, {other_files} other files, {len(files)} total")
                
                # Check for empty files
                empty_files = [f for f in files if f.stat().st_size == 0]
                if empty_files:
                    print(f"  ⚠️  Warning: {len(empty_files)} empty files detected")
            else:
                print("  No report files generated yet")
        else:
            print(f"  Report directory not found: {reports_dir}")
        
        # Show any errors
        if results.get("errors"):
            print(f"\n⚠️  ERRORS ENCOUNTERED:")
            for error in results.get("errors", []):
                error_msg = str(error).replace('<think>', '').replace('</think>', '').strip()
                print(f"   • {error_msg}")
        
        # Show success message with next steps
        print("\n" + "="*80)
        print("✅ Analysis complete! Check the data/reports directory for detailed outputs.")
        print("\n📝 Next steps:")
        print("   1. Review budget proposals in the reports directory")
        print("   2. Check detailed investigation reports for root cause analysis")
        print("   3. Implement actionable recommendations")
        print("   4. Use '--reports' option to list all generated files")
        print("="*80)
    
    def run_interactive(self):
        """Run interactive FP&A analysis"""
        print("\n" + "="*80)
        print("🤖 FP&A AGENT SYSTEM - Interactive Mode")
        print("="*80)
        print(f"📁 Reports will be saved to: {Path(settings.REPORTS_DIR)}")
        print(f"📁 Sample data: {Path(settings.DATA_DIR) / 'sample_financial_data.json'}")
        print(f"⚙️  Max Tokens: {settings.MAX_TOKENS}")
        print(f"⏱️  Timeout: {settings.REQUEST_TIMEOUT}s")
        
        while True:
            print("\nOptions:")
            print("1. Run complete analysis")
            print("2. Load documents only")
            print("3. Test variance detection")
            print("4. Test RAG retrieval")
            print("5. Generate sample data")
            print("6. Check report directory")
            print("7. Test agent connections")
            print("8. Clear report directory")
            print("9. View system settings")
            print("10. Exit")
            
            choice = input("\nEnter your choice (1-10): ").strip()
            
            if choice == "1":
                dept = input("Enter department to filter (or press Enter for all): ").strip()
                dept = None if dept == "" else dept
                self.run_complete_analysis(department=dept)
                
            elif choice == "2":
                dir_path = input(f"Enter document directory [{settings.UPLOAD_DIR}]: ").strip()
                dir_path = dir_path if dir_path else settings.UPLOAD_DIR
                docs = self.load_documents(dir_path)
                print(f"✓ Loaded {len(docs)} documents")
                if docs:
                    print("Documents loaded:")
                    for doc in docs[:5]:
                        source = doc.metadata.get('source', 'Unknown')
                        print(f"  - {source}")
                
            elif choice == "3":
                data = self.load_sample_data()
                variances = self.monitor_agent.detect_variances(data)
                sig_vars = variances.get("significant_variances", [])
                print(f"\n✓ Detected {len(sig_vars)} significant variances")
                if sig_vars:
                    print("\n📊 Top 5 Variances:")
                    for i, var in enumerate(sig_vars[:5], 1):
                        print(f"\n  {i}. {var.get('department')}: {var.get('account_name')}")
                        print(f"     Budget: ${var.get('budget', 0):,.2f}")
                        print(f"     Actual: ${var.get('actual', 0):,.2f}")
                        print(f"     Variance: ${var.get('variance_amount', 0):,.2f} ({var.get('variance_percentage', 0):.1f}%)")
                        print(f"     Reason: {var.get('reason', 'No reason')}")
                
            elif choice == "4":
                query = input("Enter search query: ").strip()
                if query:
                    print(f"\n🔍 Searching for: '{query}'")
                    results = self.rag_retriever.retrieve_relevant_documents(query)
                    print(f"✓ Found {results['total_found']} relevant documents")
                    
                    if results.get('organized_documents'):
                        for doc_type, docs in results['organized_documents'].items():
                            if docs:
                                print(f"   {doc_type.capitalize()}: {len(docs)} documents")
                                for doc in docs[:2]:
                                    source = doc.metadata.get('source', 'Unknown')
                                    preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                                    print(f"     - {source}: {preview}")
                else:
                    print("❌ Please enter a search query")
                
            elif choice == "5":
                data = self.data_loader.generate_sample_data()
                self.data_loader.save_financial_data(data, "sample_financial_data.json")
                print(f"✓ Generated {len(data)} sample records")
                print("\nSample records include:")
                for record in data[:3]:
                    print(f"  - {record['department']}: {record['account_name']} (Budget: ${record['budget']:,.2f})")
                
            elif choice == "6":
                reports_dir = Path(settings.REPORTS_DIR)
                if reports_dir.exists():
                    files = list(reports_dir.glob("*"))
                    print(f"\n📁 Report directory: {reports_dir}")
                    print(f"Total files: {len(files)}")
                    if files:
                        print("\nRecent reports (newest first):")
                        files_by_date = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
                        for f in files_by_date[:10]:
                            size = f.stat().st_size
                            size_kb = size / 1024
                            date = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                            file_type = "📄" if f.suffix == '.txt' else "📊" if f.suffix == '.json' else "📁"
                            print(f"  {file_type} {f.name} ({size_kb:.1f} KB, {date})")
                        
                        # Show statistics
                        json_files = len([f for f in files if f.suffix == '.json'])
                        txt_files = len([f for f in files if f.suffix == '.txt'])
                        other_files = len(files) - json_files - txt_files
                        print(f"\n📊 Statistics: {json_files} JSON files, {txt_files} text files, {other_files} other files")
                        
                        # Show largest files
                        if files:
                            largest_files = sorted(files, key=lambda x: x.stat().st_size, reverse=True)[:3]
                            print(f"\n📈 Largest files:")
                            for f in largest_files:
                                size_kb = f.stat().st_size / 1024
                                print(f"  - {f.name} ({size_kb:.1f} KB)")
                    else:
                        print("No report files yet")
                else:
                    print(f"Report directory does not exist: {reports_dir}")
                
            elif choice == "7":
                print("\n🔗 Testing agent connections...")
                try:
                    # Test monitor agent
                    test_response = self.monitor_agent.quick_invoke("Say 'OK'")
                    test_response = test_response.replace('<think>', '').replace('</think>', '').strip()
                    print(f"✓ Monitor Agent: {test_response[:50]}...")
                    
                    # Test investigator agent
                    test_response = self.investigator_agent.quick_invoke("Say 'OK'")
                    test_response = test_response.replace('<think>', '').replace('</think>', '').strip()
                    print(f"✓ Investigator Agent: {test_response[:50]}...")
                    
                    # Test reporter agent
                    test_response = self.reporter_agent.quick_invoke("Say 'OK'")
                    test_response = test_response.replace('<think>', '').replace('</think>', '').strip()
                    print(f"✓ Reporter Agent: {test_response[:50]}...")
                    
                    print("✅ All agents connected successfully")
                except Exception as e:
                    print(f"❌ Agent connection test failed: {e}")
                
            elif choice == "8":
                # Clear report directory (with confirmation)
                reports_dir = Path(settings.REPORTS_DIR)
                if reports_dir.exists():
                    files = list(reports_dir.glob("*"))
                    if files:
                        print(f"\n⚠️  WARNING: This will delete {len(files)} files from:")
                        print(f"   {reports_dir}")
                        print("\nFiles to be deleted:")
                        for f in files[:5]:
                            size_kb = f.stat().st_size / 1024
                            print(f"   - {f.name} ({size_kb:.1f} KB)")
                        if len(files) > 5:
                            print(f"   - ... and {len(files) - 5} more files")
                        
                        confirm = input(f"\n⚠️  Are you sure you want to delete ALL {len(files)} files? (type 'DELETE' to confirm): ").strip()
                        if confirm == 'DELETE':
                            deleted_count = 0
                            for f in files:
                                try:
                                    f.unlink()
                                    deleted_count += 1
                                except Exception as e:
                                    print(f"   Could not delete {f.name}: {e}")
                            print(f"✓ Deleted {deleted_count}/{len(files)} files")
                        else:
                            print("Operation cancelled")
                    else:
                        print("No files to delete")
                else:
                    print(f"Reports directory does not exist: {reports_dir}")
                
            elif choice == "9":
                print("\n⚙️  SYSTEM SETTINGS:")
                print("-"*40)
                print(f"   Model: {settings.MODEL_ID}")
                print(f"   LM Studio URL: {settings.LMSTUDIO_BASE_URL}")
                print(f"   Max Tokens: {settings.MAX_TOKENS}")
                print(f"   Timeout: {settings.REQUEST_TIMEOUT}s")
                print(f"   Temperature: {settings.TEMPERATURE}")
                print(f"   Data Directory: {settings.DATA_DIR}")
                print(f"   Reports Directory: {settings.REPORTS_DIR}")
                print(f"   Upload Directory: {settings.UPLOAD_DIR}")
                print(f"   Variance Threshold: {settings.VARIANCE_THRESHOLD*100}%")
                print(f"   Significant Amount: ${settings.SIGNIFICANT_AMOUNT:,.2f}")
                
            elif choice == "10":
                print("\n👋 Exiting FP&A Agent System. Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter a number between 1-10.")

async def main():
    """Main async entry point"""
    system = FPASystem()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            system.run_interactive()
        elif sys.argv[1] == "--analyze":
            department = sys.argv[2] if len(sys.argv) > 2 else None
            system.run_complete_analysis(department)
        elif sys.argv[1] == "--test":
            # Test LM Studio connection
            try:
                test_response = system.monitor_agent.quick_invoke("Say 'OK'")
                test_response = test_response.replace('<think>', '').replace('</think>', '').strip()
                print(f"✓ LM Studio connection test: {test_response}")
            except Exception as e:
                print(f"✗ LM Studio connection failed: {e}")
        elif sys.argv[1] == "--reports":
            # Show report directory
            reports_dir = Path(settings.REPORTS_DIR)
            if reports_dir.exists():
                files = list(reports_dir.glob("*"))
                print(f"Reports directory: {reports_dir}")
                print(f"Total files: {len(files)}")
                if files:
                    print("\n📊 Budget Proposals (JSON files):")
                    json_files = [f for f in files if f.suffix == '.json']
                    if json_files:
                        for f in sorted(json_files)[:15]:
                            size_kb = f.stat().st_size / 1024
                            date = datetime.fromtimestamp(f.stat().st_mtime).strftime('%m-%d %H:%M')
                            print(f"  📊 {f.name} ({size_kb:.1f} KB, {date})")
                    
                    print("\n📄 Reports (Text files):")
                    txt_files = [f for f in files if f.suffix == '.txt']
                    if txt_files:
                        for f in sorted(txt_files)[:15]:
                            size_kb = f.stat().st_size / 1024
                            date = datetime.fromtimestamp(f.stat().st_mtime).strftime('%m-%d %H:%M')
                            print(f"  📄 {f.name} ({size_kb:.1f} KB, {date})")
                    
                    # Statistics
                    json_count = len(json_files)
                    txt_count = len(txt_files)
                    other_count = len(files) - json_count - txt_count
                    total_size = sum(f.stat().st_size for f in files) / 1024  # KB
                    
                    print(f"\n📈 STATISTICS:")
                    print(f"  Budget Proposals (JSON): {json_count} files")
                    print(f"  Reports (Text): {txt_count} files")
                    print(f"  Other files: {other_count} files")
                    print(f"  Total files: {len(files)}")
                    print(f"  Total size: {total_size:.1f} KB ({total_size/1024:.2f} MB)")
                    
                    # Check for empty files
                    empty_files = [f for f in files if f.stat().st_size == 0]
                    if empty_files:
                        print(f"\n⚠️  WARNING: {len(empty_files)} empty files detected:")
                        for f in empty_files[:5]:
                            print(f"  - {f.name}")
                        if len(empty_files) > 5:
                            print(f"  - ... and {len(empty_files) - 5} more")
                else:
                    print("No report files yet")
            else:
                print(f"Reports directory does not exist: {reports_dir}")
        elif sys.argv[1] == "--clear-reports":
            # Clear report directory (with confirmation)
            reports_dir = Path(settings.REPORTS_DIR)
            if reports_dir.exists():
                files = list(reports_dir.glob("*"))
                if files:
                    confirm = input(f"Delete {len(files)} files from {reports_dir}? (y/N): ").strip().lower()
                    if confirm == 'y':
                        for f in files:
                            f.unlink()
                        print(f"✓ Deleted {len(files)} files")
                    else:
                        print("Operation cancelled")
                else:
                    print("No files to delete")
            else:
                print(f"Reports directory does not exist: {reports_dir}")
        elif sys.argv[1] == "--help":
            print("Usage: python main.py [OPTION]")
            print("\nOptions:")
            print("  --interactive     Run in interactive mode")
            print("  --analyze [DEPT]  Run complete analysis (optional: department filter)")
            print("  --test            Test LM Studio connection")
            print("  --reports         Show detailed report directory contents")
            print("  --clear-reports   Clear report directory (with confirmation)")
            print("  --help            Show this help message")
        else:
            print(f"❌ Unknown command: {sys.argv[1]}")
            print("Usage: python main.py [--interactive | --analyze [department] | --test | --reports | --help]")
    else:
        # Default: run complete analysis
        print("🚀 Starting FP&A Agent System...")
        print(f"📁 Reports will be saved to: {Path(settings.REPORTS_DIR)}")
        print(f"⚙️  Max Tokens: {settings.MAX_TOKENS}")
        print(f"⏱️  Timeout: {settings.REQUEST_TIMEOUT}s")
        print("="*50)
        system.run_complete_analysis()

if __name__ == "__main__":
    # Run async main
    asyncio.run(main())