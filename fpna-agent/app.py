#!/usr/bin/env python3
"""
Streamlit UI for FP&A Agent System
"""

import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

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
from src.analysis.variance_engine import VarianceEngine
from src.analysis.trend_analyzer import TrendAnalyzer

# Page configuration
st.set_page_config(
    page_title="FP&A Agent System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        color-scheme: dark;
        font-family: 'Inter', sans-serif;
        background-color: #0A0A0A;
        color: #FFFFFF;
    }

    body, .stApp, .css-1d391kg, .css-1aumxhk, .main {
        background-color: #0A0A0A !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    header, footer, nav, .css-1o6f6c9, .css-1y4p8pa {
        background: transparent !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(10, 10, 10, 0.75) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 28px 80px rgba(0, 0, 0, 0.45);
    }

    .css-18e3th9, .css-12w0qpk, .css-10trblm {
        background: transparent !important;
    }

    .main-header {
        font-size: 3rem;
        font-weight: 400;
        line-height: 1.1;
        letter-spacing: -0.05em;
        margin-bottom: 1rem;
        color: #FFFFFF;
    }

    .sub-header {
        font-size: 1.5rem;
        font-weight: 300;
        line-height: 1.5;
        color: rgba(255, 255, 255, 0.72);
        margin-bottom: 1rem;
    }

    .hero-panel {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        backdrop-filter: blur(24px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.24);
        padding: 2rem;
        margin-bottom: 2rem;
    }

    .hero-copy {
        max-width: 64rem;
        color: rgba(255, 255, 255, 0.72);
        font-size: 1rem;
        line-height: 1.75;
        margin-top: 0.75rem;
    }

    .hero-text {
        color: rgba(255, 255, 255, 0.72);
        font-size: 1rem;
        line-height: 1.75;
        margin-top: 0.5rem;
    }

    .metric-card, .glass-card {
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 1.4rem;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.18);
        color: rgba(255, 255, 255, 0.94);
        margin-bottom: 1.5rem;
    }

    .metric-card {
        border-left: 4px solid rgba(229, 169, 60, 0.75);
    }

    .gold-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.4rem;
        padding: 0.55rem 1.2rem;
        border-radius: 999px;
        border: 1px solid rgba(229, 169, 60, 0.19);
        background: rgba(229, 169, 60, 0.1);
        color: #E5A93C;
        font-weight: 600;
        letter-spacing: 0.08em;
        margin-bottom: 1rem;
        text-transform: uppercase;
        font-size: 0.8rem;
    }

    h1, h2, h3, h4, h5 {
        color: #FFFFFF !important;
    }

    p, label, div, a {
        color: rgba(255, 255, 255, 0.86) !important;
    }

    .stButton>button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        border-radius: 999px !important;
        border: 1px solid rgba(229, 169, 60, 0.25) !important;
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.18) !important;
        padding: 0.75rem 1.45rem !important;
        min-height: 48px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease !important;
    }

    .stButton>button span {
        color: #FFFFFF !important;
    }

    .stButton>button:focus-visible {
        outline: 2px solid rgba(229, 169, 60, 0.85) !important;
        outline-offset: 3px !important;
    }

    .stButton>button:hover {
        transform: translateY(-1px) !important;
        background: rgba(255, 255, 255, 0.14) !important;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.22) !important;
    }

    .css-1g7m0tk, .css-1v3fvcr, .css-k1vhr4 {
        border-radius: 24px !important;
    }

    div.row-widget.stRadio > label, div.row-widget.stCheckbox > label, div.row-widget.stSelectbox > label {
        color: rgba(255, 255, 255, 0.92) !important;
    }

    .css-1fcbym4, .css-18ni7ap, .css-1u9z7r6 {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 18px !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(10, 10, 10, 0.92) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        backdrop-filter: blur(24px);
        box-shadow: 0 24px 60px rgba(0,0,0,0.24) !important;
    }

    .css-1avcm0n {
        max-width: 1480px !important;
        margin: 0 auto !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }

    .stButton>button:focus-visible, button:focus-visible {
        outline: 2px solid rgba(229, 169, 60, 0.85) !important;
        outline-offset: 3px !important;
    }

    .css-1g7m0tk, .css-1v3fvcr, .css-k1vhr4 {
        border-radius: 24px !important;
    }

    div.row-widget.stRadio > label, div.row-widget.stCheckbox > label, div.row-widget.stSelectbox > label {
        color: rgba(255, 255, 255, 0.92) !important;
    }

    .css-1fcbym4, .css-18ni7ap, .css-1u9z7r6 {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

class FPAApp:
    """Streamlit application for FP&A Agent System"""
    
    def __init__(self):
        self.initialize_session_state()
        
        # Initialize system components
        if 'system' not in st.session_state:
            with st.spinner("Initializing FP&A System..."):
                try:
                    self.initialize_system()
                    st.session_state.system_initialized = True
                    st.success("✓ FP&A System initialized successfully")
                except Exception as e:
                    st.error(f"Failed to initialize system: {e}")
                    st.session_state.system_initialized = False
        else:
            # Restore components stored in session state to instance attributes
            system = st.session_state.get('system', {})
            self.data_loader = system.get('data_loader')
            self.document_loader = system.get('document_loader')
            self.monitor_agent = system.get('monitor_agent')
            self.vector_store = system.get('vector_store')
            self.rag_retriever = system.get('rag_retriever')
            self.investigator_agent = system.get('investigator_agent')
            self.reporter_agent = system.get('reporter_agent')
            self.workflow = system.get('workflow')
            self.variance_engine = system.get('variance_engine')
            self.trend_analyzer = system.get('trend_analyzer')
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'system_initialized': False,
            'financial_data': None,
            'documents_loaded': False,
            'analysis_results': None,
            'current_page': 'dashboard',
            'uploaded_files': [],
            'selected_department': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def initialize_system(self):
        """Initialize FP&A system components"""
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
        
        # Initialize analyzers
        self.variance_engine = VarianceEngine()
        self.trend_analyzer = TrendAnalyzer()
        
        # Store in session state
        st.session_state.system = {
            'data_loader': self.data_loader,
            'document_loader': self.document_loader,
            'monitor_agent': self.monitor_agent,
            'vector_store': self.vector_store,
            'rag_retriever': self.rag_retriever,
            'investigator_agent': self.investigator_agent,
            'reporter_agent': self.reporter_agent,
            'workflow': self.workflow,
            'variance_engine': self.variance_engine,
            'trend_analyzer': self.trend_analyzer
        }
    
    def render_sidebar(self):
        """Render the sidebar"""
        with st.sidebar:
            st.markdown("## 📊 FP&A Agent System")
            st.markdown("---")
            
            # Navigation
            page = st.radio(
                "Navigation",
                ["Dashboard", "Data Management", "Variance Analysis", 
                 "Document Investigation", "Reports", "Settings"],
                key="nav_radio"
            )
            
            # Map radio selection to page
            page_map = {
                "Dashboard": "dashboard",
                "Data Management": "data_management",
                "Variance Analysis": "variance_analysis",
                "Document Investigation": "document_investigation",
                "Reports": "reports",
                "Settings": "settings"
            }
            st.session_state.current_page = page_map[page]
            
            st.markdown("---")
            
            # System Status
            st.markdown("### System Status")
            
            if st.session_state.system_initialized:
                st.success("✅ System Ready")
                
                # Document count
                doc_count = self.vector_store.get_document_count()
                st.metric("Documents Loaded", doc_count)
            else:
                st.error("❌ System Not Ready")
            
            st.markdown("---")
            
            # Quick Actions
            st.markdown("### Quick Actions")
            
            if st.button("🔄 Refresh System", use_container_width=True):
                st.rerun()
            
            if st.button("📊 Run Full Analysis", use_container_width=True):
                st.session_state.run_full_analysis = True
            
            st.markdown("---")
            
            # Department Filter
            st.markdown("### Department Filter")
            departments = ["All", "Marketing", "Sales", "R&D", "Operations", "IT"]
            selected_dept = st.selectbox(
                "Select Department",
                departments,
                index=0
            )
            st.session_state.selected_department = None if selected_dept == "All" else selected_dept
    
    def render_dashboard(self):
        """Render the dashboard page"""
        st.markdown('<div class="hero-panel">\n'
                    '  <div class="gold-pill">Command Center</div>\n'
                    '  <div class="main-header">FP&A Agent Dashboard</div>\n'
                    '  <div class="hero-copy">\n'
                    '    A premium asset management interface built for secure financial operations, blending dark depth with high-contrast gold accents.\n'
                    '    The dashboard surfaces real-time variance intelligence, document investigation, and strategic reporting in a glassmorphic layout.\n'
                    '  </div>\n'
                    '</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card">\n'
                    '  <div style="display:flex;gap:1rem;flex-wrap:wrap;align-items:center;justify-content:space-between;">\n'
                    '    <div>\n'
                    '      <h3 style="margin:0;color:#FFFFFF;">Command Center</h3>\n'
                    '      <p style="margin:0;color:rgba(255,255,255,0.72);">Immediate access to variance detection, document validation, and report generation.</p>\n'
                    '    </div>\n'
                    '    <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">\n'
                    '      <span class="gold-pill">Variance</span>\n'
                    '      <span class="gold-pill">Investigation</span>\n'
                    '      <span class="gold-pill">Reporting</span>\n'
                    '    </div>\n'
                    '  </div>\n'
                    '</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📈 Variance Analysis")
            if st.button("Run Variance Detection", use_container_width=True):
                self.run_variance_analysis()
        
        with col2:
            st.markdown("### 🔍 Document Investigation")
            if st.button("Investigate Documents", use_container_width=True):
                st.session_state.current_page = "document_investigation"
                st.rerun()
        
        with col3:
            st.markdown("### 📋 Generate Reports")
            if st.button("Create Executive Report", use_container_width=True):
                self.generate_executive_report()
        
        st.markdown("---")
        
        # Recent Activity
        st.markdown('<div class="glass-card">\n'
                    '  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">\n'
                    '    <div>\n'
                    '      <h3 style="margin:0;color:#FFFFFF;">Recent Activity</h3>\n'
                    '      <p style="margin:0;color:rgba(255,255,255,0.7);">Live operational intelligence and the latest system actions.</p>\n'
                    '    </div>\n'
                    '  </div>\n'
                    '</div>', unsafe_allow_html=True)
        
        if st.session_state.get('analysis_results'):
            results = st.session_state.analysis_results
            metrics = results.get('metrics', {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Accounts",
                    metrics.get('total_variances_analyzed', 0)
                )
            
            with col2:
                st.metric(
                    "Significant Variances",
                    metrics.get('significant_variances_found', 0)
                )
            
            with col3:
                st.metric(
                    "Investigations",
                    metrics.get('investigations_completed', 0)
                )
            
            with col4:
                st.metric(
                    "Processing Time",
                    metrics.get('processing_time', 'N/A')
                )
            
            # Display top variances
            if results.get('results', {}).get('variance_analysis'):
                variance_data = results['results']['variance_analysis']
                sig_vars = variance_data.get('significant_variances', [])
                
                if sig_vars:
                    st.markdown("#### Top Significant Variances")
                    df = pd.DataFrame(sig_vars)[:5]
                    st.dataframe(df[['department', 'account_name', 'variance_amount', 'variance_percentage', 'reason']])
        else:
            st.info("No analysis results yet. Run an analysis to see data here.")
        
        # Quick Analysis
        st.markdown('<div class="glass-card">\n'
                    '  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">\n'
                    '    <div>\n'
                    '      <h3 style="margin:0;color:#FFFFFF;">Quick Actions</h3>\n'
                    '      <p style="margin:0;color:rgba(255,255,255,0.7);">Fast access to sample data and validation tests.</p>\n'
                    '    </div>\n'
                    '  </div>\n'
                    '</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Load Sample Data", use_container_width=True):
                self.load_sample_data()
        
        with col2:
            if st.button("Test LM Studio", use_container_width=True):
                self.test_lm_studio()
    
    def render_data_management(self):
        """Render data management page"""
        st.markdown('<div class="hero-panel">\n'
                    '  <div class="gold-pill">Data Intelligence</div>\n'
                    '  <div class="main-header">Data Management</div>\n'
                    '  <div class="hero-copy">\n'
                    '    Secure upload and governance with glassmorphic panels, native file controls, and premium data preview surfaces.\n'
                    '  </div>\n'
                    '</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📁 Upload Data", "📊 Generate Sample", "🗃️ Document Management"])
        
        with tab1:
            st.markdown("### Upload Financial Data")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose a CSV or JSON file",
                type=['csv', 'json'],
                key="data_uploader"
            )
            
            if uploaded_file is not None:
                try:
                    # Save uploaded file
                    file_path = os.path.join(settings.UPLOAD_DIR, uploaded_file.name)
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Load data
                    if uploaded_file.name.endswith('.csv'):
                        data = self.data_loader.load_csv_data(file_path)
                    else:
                        data = self.data_loader.load_json_data(file_path)
                    
                    st.session_state.financial_data = data
                    st.success(f"✓ Loaded {len(data)} financial records from {uploaded_file.name}")
                    
                    # Display preview
                    st.markdown("#### Data Preview")
                    df = pd.DataFrame([item.model_dump() for item in data[:10]])
                    st.dataframe(df)
                    
                except Exception as e:
                    st.error(f"Error loading file: {e}")
        
        with tab2:
            st.markdown("### Generate Sample Data")
            
            if st.button("Generate Sample Financial Data", use_container_width=True):
                with st.spinner("Generating sample data..."):
                    data = self.data_loader.generate_sample_data()
                    self.data_loader.save_financial_data(data, "sample_financial_data.json")
                    st.session_state.financial_data = data
                    
                    st.success(f"✓ Generated {len(data)} sample records")
                    
                    # Display preview
                    st.markdown("#### Sample Data Preview")
                    df = pd.DataFrame([item.model_dump() for item in data[:10]])
                    st.dataframe(df)
        
        with tab3:
            st.markdown("### Document Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Upload Documents")
                uploaded_docs = st.file_uploader(
                    "Choose documents for investigation",
                    type=['pdf', 'txt', 'csv', 'docx', 'xlsx', 'json'],
                    accept_multiple_files=True,
                    key="doc_uploader"
                )
                
                if uploaded_docs:
                    if st.button("Process Documents", use_container_width=True):
                        with st.spinner("Processing documents..."):
                            processed_count = 0
                            for doc in uploaded_docs:
                                try:
                                    # Save document
                                    file_path = os.path.join(settings.UPLOAD_DIR, doc.name)
                                    with open(file_path, 'wb') as f:
                                        f.write(doc.getbuffer())
                                    
                                    # Load into vector store
                                    documents = self.document_loader.load_document(file_path)
                                    self.vector_store.add_documents(documents)
                                    processed_count += len(documents)
                                    
                                except Exception as e:
                                    st.error(f"Error processing {doc.name}: {e}")
                            
                            st.success(f"✓ Processed {processed_count} documents from {len(uploaded_docs)} files")
                            st.session_state.documents_loaded = True
            
            with col2:
                st.markdown("#### Document Statistics")
                
                doc_count = self.vector_store.get_document_count()
                st.metric("Total Documents", doc_count)
                
                if st.button("Clear All Documents", type="secondary"):
                    with st.spinner("Clearing documents..."):
                        self.vector_store.clear()
                        st.success("✓ All documents cleared")
                        st.session_state.documents_loaded = False
                
                if st.button("Load All Documents", type="secondary"):
                    with st.spinner("Loading documents..."):
                        documents = self.document_loader.load_directory(settings.UPLOAD_DIR)
                        self.vector_store.add_documents(documents)
                        st.success(f"✓ Loaded {len(documents)} documents")
                        st.session_state.documents_loaded = True
    
    def render_variance_analysis(self):
        """Render variance analysis page"""
        st.markdown('<div class="hero-panel">\n'
                    '  <div class="gold-pill">Performance Terminal</div>\n'
                    '  <div class="main-header">Variance Analysis</div>\n'
                    '  <div class="hero-copy">\n'
                    '    Evaluate deviations with premium analytics panels and actionable insights outlined in a high-contrast financial command center.\n'
                    '  </div>\n'
                    '</div>', unsafe_allow_html=True)
        
        if not st.session_state.financial_data:
            st.warning("No financial data loaded. Please load data first.")
            return
        
        # Analysis controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            threshold = st.slider(
                "Variance Threshold (%)",
                min_value=1,
                max_value=50,
                value=int(settings.VARIANCE_THRESHOLD * 100),
                key="threshold_slider"
            )
        
        with col2:
            significant_amount = st.number_input(
                "Significant Amount ($)",
                min_value=1000,
                max_value=100000,
                value=int(settings.SIGNIFICANT_AMOUNT),
                step=1000,
                key="amount_input"
            )
        
        with col3:
            department = st.session_state.selected_department
            if department:
                st.info(f"Department Filter: {department}")
        
        if st.button("Run Variance Analysis", type="primary", use_container_width=True):
            self.run_variance_analysis(threshold, significant_amount, department)
        
        # Display results if available
        if st.session_state.get('analysis_results'):
            self.display_variance_results()
    
    def run_variance_analysis(self, threshold=None, significant_amount=None, department=None):
        """Run variance analysis"""
        if not st.session_state.financial_data:
            st.error("No financial data available")
            return
        
        with st.spinner("Running variance analysis..."):
            try:
                # Update settings if provided
                if threshold:
                    settings.VARIANCE_THRESHOLD = threshold / 100
                if significant_amount:
                    settings.SIGNIFICANT_AMOUNT = significant_amount
                
                # Run analysis
                results = st.session_state.system['workflow'].run(
                    financial_data=st.session_state.financial_data,
                    department_filter=department
                )
                
                st.session_state.analysis_results = results
                st.success("✓ Analysis completed successfully")
                
            except Exception as e:
                st.error(f"Analysis failed: {e}")
    
    def display_variance_results(self):
        """Display variance analysis results"""
        results = st.session_state.analysis_results
        variance_results = results.get('results', {}).get('variance_analysis', {})
        
        if not variance_results:
            st.info("No variance results to display")
            return
        
        # Summary metrics
        metrics = results['metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Accounts Analyzed", metrics['total_variances_analyzed'])
        
        with col2:
            st.metric("Significant Variances", metrics['significant_variances_found'])
        
        with col3:
            significance_rate = (metrics['significant_variances_found'] / 
                               metrics['total_variances_analyzed'] * 100) if metrics['total_variances_analyzed'] > 0 else 0
            st.metric("Significance Rate", f"{significance_rate:.1f}%")
        
        with col4:
            st.metric("Processing Time", metrics['processing_time'])
        
        st.markdown("---")
        
        # Variance Summary
        st.markdown("### Variance Summary")
        summary = variance_results.get('summary', 'No summary available')
        st.markdown(f'<div class="metric-card">{summary[:1000]}...</div>', unsafe_allow_html=True)
        
        # Significant Variances Table
        st.markdown("### Significant Variances")
        sig_vars = variance_results.get('significant_variances', [])
        
        if sig_vars:
            df = pd.DataFrame(sig_vars)
            
            # Add color coding
            def color_variance(val):
                color = 'red' if val > 0 else 'green'
                return f'color: {color}'
            
            styled_df = df.style.applymap(color_variance, subset=['variance_amount'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Variance by department
                if 'department' in df.columns:
                    dept_variance = df.groupby('department')['variance_amount'].sum().reset_index()
                    fig = px.bar(dept_variance, x='department', y='variance_amount',
                                title='Total Variance by Department',
                                color='variance_amount',
                                color_continuous_scale='RdYlGn_r')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Variance distribution
                fig = px.histogram(df, x='variance_percentage',
                                 title='Distribution of Variance Percentages',
                                 nbins=20)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No significant variances found!")
    
    def render_document_investigation(self):
        """Render document investigation page"""
        st.markdown('<div class="hero-panel">\n'
                    '  <div class="gold-pill">Investigative Console</div>\n'
                    '  <div class="main-header">Document Investigation</div>\n'
                    '  <div class="hero-copy">\n'
                    '    Search, validate, and link documents with a premium investigatory flow designed for audit-grade clarity.\n'
                    '  </div>\n'
                    '</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔍 Search Documents", "📄 Investigate Variance"])
        
        with tab1:
            st.markdown("### Document Search")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                query = st.text_input("Search query", placeholder="e.g., invoice for marketing Q4")
            
            with col2:
                doc_types = st.multiselect(
                    "Document Types",
                    ["invoices", "contracts", "approvals", "reports", "other"],
                    default=["invoices", "contracts", "approvals"]
                )
            
            if st.button("Search Documents", use_container_width=True) and query:
                with st.spinner("Searching documents..."):
                    try:
                        results = self.rag_retriever.retrieve_relevant_documents(query, doc_types)
                        
                        st.markdown(f"#### Found {results['total_found']} relevant documents")
                        
                        # Display organized results
                        for doc_type, docs in results.get('organized_documents', {}).items():
                            if docs:
                                with st.expander(f"{doc_type.title()} ({len(docs)} documents)"):
                                    for doc in docs[:5]:  # Show first 5
                                        st.markdown(f"**Source:** {doc.metadata.get('source', 'Unknown')}")
                                        st.markdown(f"**Preview:** {doc.page_content[:200]}...")
                                        st.markdown("---")
                        
                        # Display summary
                        if results.get('summary'):
                            st.markdown("#### Relevance Summary")
                            st.markdown(f'<div class="metric-card">{results["summary"]}</div>', unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"Search failed: {e}")
        
        with tab2:
            st.markdown("### Investigate Specific Variance")
            
            if not st.session_state.get('analysis_results'):
                st.info("Please run variance analysis first")
                return
            
            variance_results = st.session_state.analysis_results['results']['variance_analysis']
            sig_vars = variance_results.get('significant_variances', [])
            
            if not sig_vars:
                st.success("No variances to investigate!")
                return
            
            # Select variance to investigate
            variance_options = [
                f"{v.get('department')} - {v.get('account_name')} (${v.get('variance_amount', 0):,.2f})"
                for v in sig_vars[:10]
            ]
            
            selected_variance = st.selectbox(
                "Select variance to investigate",
                variance_options,
                key="variance_select"
            )
            
            if selected_variance and st.button("Investigate Variance", use_container_width=True):
                with st.spinner("Investigating variance..."):
                    try:
                        # Find the selected variance
                        idx = variance_options.index(selected_variance)
                        variance = sig_vars[idx]
                        department = variance.get('department')
                        
                        # Run investigation
                        investigation = self.investigator_agent.investigate_variance(
                            variance_details=variance,
                            department=department
                        )
                        
                        # Display results
                        st.markdown("#### Investigation Results")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Evidence Found", investigation.get('evidence_found', 0))
                        
                        with col2:
                            confidence = investigation.get('investigation_result', {}).get('confidence', 0)
                            st.metric("Confidence", f"{confidence:.1f}%")
                        
                        # Root cause analysis
                        st.markdown("#### Root Cause Analysis")
                        investigation_data = investigation.get('investigation_result', {})
                        root_cause = investigation_data.get('root_cause_analysis', 'No analysis available')
                        st.markdown(f'<div class="metric-card">{root_cause}</div>', unsafe_allow_html=True)
                        
                        # Recommendations
                        st.markdown("#### Recommendations")
                        recommendations = investigation_data.get('recommendations', [])
                        
                        for i, rec in enumerate(recommendations, 1):
                            if isinstance(rec, dict):
                                action = rec.get('action', '')
                                priority = rec.get('priority', 'MEDIUM')
                                owner = rec.get('owner', '')
                                timeline = rec.get('timeline', '')
                            else:
                                action = str(rec)
                                priority = 'MEDIUM'
                                owner = department or ''
                                timeline = 'Review'

                            priority_color = {
                                'HIGH': 'red',
                                'MEDIUM': 'orange',
                                'LOW': 'green'
                            }.get(priority, 'black')
                            
                            st.markdown(f"""
                            <div style="border-left: 4px solid {priority_color}; padding-left: 10px; margin-bottom: 10px;">
                                <strong>{i}. {action}</strong><br>
                                Priority: <span style="color: {priority_color}">{priority}</span> | 
                                Owner: {owner} | 
                                Timeline: {timeline}
                            </div>
                            """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Investigation failed: {e}")
    
    def render_reports(self):
        """Render reports page"""
        st.markdown('<div class="hero-panel">\n'
                    '  <div class="gold-pill">Strategy Cards</div>\n'
                    '  <div class="main-header">Reports & Proposals</div>\n'
                    '  <div class="hero-copy">\n'
                    '    Generate executive narratives, budget proposals, and deep-dive reports within a premium financial storytelling workspace.\n'
                    '  </div>\n'
                    '</div>', unsafe_allow_html=True)
        
        if not st.session_state.get('analysis_results'):
            st.info("Please run analysis first to generate reports")
            return
        
        results = st.session_state.analysis_results
        
        tab1, tab2, tab3 = st.tabs(["📋 Executive Summary", "📑 Budget Proposals", "📊 Detailed Reports"])
        
        with tab1:
            st.markdown("### Executive Summary")
            
            if results['results'].get('executive_summary'):
                summary = results['results']['executive_summary']
                
                if summary.get('status') == 'SUCCESS':
                    st.markdown(f'<div class="metric-card">{summary.get("summary", "")}</div>', unsafe_allow_html=True)
                    
                    # Key insights
                    st.markdown("#### Key Insights")
                    insights = summary.get('key_insights', [])
                    for insight in insights:
                        st.markdown(f"- {insight}")
                    
                    # Recommendations
                    st.markdown("#### Top Recommendations")
                    recs = summary.get('recommendations', [])
                    for rec in recs[:5]:
                        st.markdown(f"- {rec}")
                    
                    # Download button
                    summary_text = f"""
                    FP&A Executive Summary
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    
                    {summary.get('summary', '')}
                    
                    Key Insights:
                    {chr(10).join([f'- {i}' for i in insights])}
                    
                    Recommendations:
                    {chr(10).join([f'- {r}' for r in recs])}
                    """
                    
                    st.download_button(
                        label="Download Executive Summary",
                        data=summary_text,
                        file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("Failed to generate executive summary")
            else:
                st.info("No executive summary available. Run a complete analysis first.")
        
        with tab2:
            st.markdown("### Budget Adjustment Proposals")
            
            proposals = results['results'].get('budget_proposals', [])
            
            if proposals:
                for i, proposal in enumerate(proposals, 1):
                    account = proposal.get('account', 'Unknown Account')
                    with st.expander(f"Proposal {i}: {account}"):
                        st.markdown(f'<div class="metric-card">{proposal.get("justification", "")}</div>', unsafe_allow_html=True)

                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Department", proposal.get('department', 'Unknown'))
                        
                        with col2:
                            st.metric("Variance Amount", f"${proposal.get('variance_amount', 0):,.2f}")
                        
                        with col3:
                            st.metric("Confidence", f"{proposal.get('investigation_confidence', 0):.1f}%")

                        st.metric("Proposed Budget", f"${proposal.get('proposed_budget', 0):,.2f}")
                        
                        # Download button
                        proposal_text = (
                            f"Budget Adjustment Proposal\n\n"
                            f"Department: {proposal.get('department', 'Unknown')}\n"
                            f"Account: {proposal.get('account', 'Unknown')}\n"
                            f"Current Budget: ${proposal.get('current_budget', 0):,.2f}\n"
                            f"Actual Spend: ${proposal.get('actual_spend', 0):,.2f}\n"
                            f"Variance: ${proposal.get('variance_amount', 0):,.2f}\n"
                            f"Proposed Budget: ${proposal.get('proposed_budget', 0):,.2f}\n"
                            f"Adjustment: ${proposal.get('adjustment_amount', 0):,.2f} ({proposal.get('adjustment_type', 'adjustment')})\n\n"
                            f"Justification:\n{proposal.get('justification', '')}\n"
                        )
                        st.download_button(
                            label=f"Download Proposal {i}",
                            data=proposal_text,
                            file_name=f"budget_proposal_{i}_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain",
                            key=f"proposal_dl_{i}"
                        )
            else:
                st.info("No budget proposals generated. Run investigations with high confidence findings.")
        
        with tab3:
            st.markdown("### Detailed Analysis Reports")
            
            # Variance analysis report
            st.markdown("#### Variance Analysis Report")
            
            if results['results'].get('variance_analysis'):
                variance_data = results['results']['variance_analysis']
                
                # Create report
                report_text = self.create_variance_report(variance_data, results['metrics'])
                
                st.markdown(f'<div class="metric-card">{report_text[:2000]}...</div>', unsafe_allow_html=True)
                
                st.download_button(
                    label="Download Variance Report",
                    data=report_text,
                    file_name=f"variance_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            
            # Investigation reports
            st.markdown("#### Investigation Reports")
            investigation_results = results['results'].get('investigation_results', [])
            
            if investigation_results:
                for i, investigation in enumerate(investigation_results[:3], 1):
                    with st.expander(f"Investigation Report {i}"):
                        variance = investigation.get('variance_details', {})
                        st.markdown(f"**Account:** {variance.get('account_name', 'Unknown')}")
                        st.markdown(f"**Department:** {investigation.get('department', 'Unknown')}")
                        st.markdown(f"**Variance:** ${variance.get('variance_amount', 0):,.2f}")
                        
                        root_cause = investigation.get('investigation_result', {}).get('root_cause_analysis', '')
                        st.markdown(f'<div style="background-color: #F8FAFC; padding: 1rem; border-radius: 0.5rem;">{root_cause[:1000]}...</div>', unsafe_allow_html=True)
    
    def create_variance_report(self, variance_data, metrics):
        """Create variance analysis report"""
        report = f"""
        FP&A Variance Analysis Report
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        EXECUTIVE SUMMARY
        =================
        Total accounts analyzed: {metrics['total_variances_analyzed']}
        Significant variances found: {metrics['significant_variances_found']}
        Investigations completed: {metrics['investigations_completed']}
        Processing time: {metrics['processing_time']}
        
        ANALYSIS SUMMARY
        ================
        {variance_data.get('summary', 'No summary available')}
        
        SIGNIFICANT VARIANCES
        =====================
        """
        
        sig_vars = variance_data.get('significant_variances', [])
        for i, var in enumerate(sig_vars[:10], 1):
            report += f"""
            {i}. {var.get('department')} - {var.get('account_name')}
                Period: {var.get('period')}
                Budget: ${var.get('budget', 0):,.2f}
                Actual: ${var.get('actual', 0):,.2f}
                Variance: ${var.get('variance_amount', 0):,.2f} ({var.get('variance_percentage', 0):.1f}%)
                Reason: {var.get('reason', 'Not specified')}
            """
        
        return report
    
    def render_settings(self):
        """Render settings page"""
        st.markdown('<div class="hero-panel">\n'
                    '  <div class="gold-pill">Control Plane</div>\n'
                    '  <div class="main-header">System Settings</div>\n'
                    '  <div class="hero-copy">\n'
                    '    Tune the FP&A engine, LM Studio parameters, and vector store configuration with premium visual fidelity.\n'
                    '  </div>\n'
                    '</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["⚙️ System Configuration", "🤖 Agent Settings", "🗄️ Vector Store"])
        
        with tab1:
            st.markdown("### LM Studio Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                base_url = st.text_input(
                    "LM Studio Base URL",
                    value=settings.LMSTUDIO_BASE_URL,
                    help="URL where LM Studio server is running"
                )
            
            with col2:
                model_id = st.text_input(
                    "Model ID",
                    value=settings.MODEL_ID,
                    help="Model name in LM Studio"
                )
            
            st.markdown("### File Paths")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                data_dir = st.text_input("Data Directory", value=settings.DATA_DIR)
            
            with col2:
                upload_dir = st.text_input("Upload Directory", value=settings.UPLOAD_DIR)
            
            with col3:
                reports_dir = st.text_input("Reports Directory", value=settings.REPORTS_DIR)
            
            if st.button("Save Configuration", type="primary"):
                # Note: In production, you would save these to a config file
                st.success("Configuration saved (note: requires app restart to take effect)")
        
        with tab2:
            st.markdown("### Agent Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    value=settings.TEMPERATURE,
                    step=0.1,
                    help="Higher values make output more random"
                )
                
                max_tokens = st.number_input(
                    "Max Tokens",
                    min_value=512,
                    max_value=8192,
                    value=settings.MAX_TOKENS,
                    step=512
                )
            
            with col2:
                max_docs = st.number_input(
                    "Max Retrieval Documents",
                    min_value=1,
                    max_value=50,
                    value=settings.MAX_RETRIEVAL_DOCS,
                    step=1
                )
            
            st.markdown("### Financial Thresholds")
            
            col1, col2 = st.columns(2)
            
            with col1:
                variance_threshold = st.slider(
                    "Variance Threshold (%)",
                    min_value=1,
                    max_value=50,
                    value=int(settings.VARIANCE_THRESHOLD * 100),
                    step=1
                )
            
            with col2:
                significant_amount = st.number_input(
                    "Significant Amount ($)",
                    min_value=1000,
                    max_value=100000,
                    value=int(settings.SIGNIFICANT_AMOUNT),
                    step=1000
                )
            
            if st.button("Save Agent Settings", type="primary"):
                settings.TEMPERATURE = temperature
                settings.MAX_TOKENS = max_tokens
                settings.MAX_RETRIEVAL_DOCS = max_docs
                settings.VARIANCE_THRESHOLD = variance_threshold / 100
                settings.SIGNIFICANT_AMOUNT = significant_amount
                st.success("Agent settings saved")
        
        with tab3:
            st.markdown("### Vector Store Settings")
            
            vector_db_type = st.selectbox(
                "Vector Database",
                ["chroma", "pinecone"],
                index=0 if settings.VECTOR_DB_TYPE == "chroma" else 1
            )
            
            if vector_db_type == "chroma":
                persist_dir = st.text_input(
                    "Chroma Persistence Directory",
                    value=settings.CHROMA_PERSIST_DIR
                )
                
                if st.button("Clear Vector Store", type="secondary"):
                    with st.spinner("Clearing vector store..."):
                        self.vector_store.clear()
                        st.success("Vector store cleared")
            
            else:  # pinecone
                col1, col2 = st.columns(2)
                
                with col1:
                    pinecone_key = st.text_input(
                        "Pinecone API Key",
                        value=settings.PINECONE_API_KEY or "",
                        type="password"
                    )
                
                with col2:
                    pinecone_env = st.text_input(
                        "Pinecone Environment",
                        value=settings.PINECONE_ENVIRONMENT or ""
                    )
                
                index_name = st.text_input(
                    "Pinecone Index Name",
                    value=settings.PINECONE_INDEX_NAME
                )
            
            doc_count = self.vector_store.get_document_count()
            st.metric("Documents in Vector Store", doc_count)
    
    def load_sample_data(self):
        """Load sample data"""
        with st.spinner("Loading sample data..."):
            data = self.data_loader.generate_sample_data()
            st.session_state.financial_data = data
            st.success(f"✓ Generated {len(data)} sample records")
    
    def test_lm_studio(self):
        """Test LM Studio connection"""
        with st.spinner("Testing LM Studio connection..."):
            try:
                test_response = self.monitor_agent.invoke("Hello, please respond with 'OK' if you can hear me.")
                st.success(f"✓ LM Studio connection successful")
                st.info(f"Response: {test_response[:100]}...")
            except Exception as e:
                st.error(f"✗ LM Studio connection failed: {e}")
    
    def generate_executive_report(self):
        """Generate executive report"""
        if not st.session_state.get('analysis_results'):
            st.error("Please run analysis first")
            return
        
        with st.spinner("Generating executive report..."):
            try:
                investigation_results = st.session_state.analysis_results['results'].get('investigation_results', [])
                
                if investigation_results:
                    summary = self.reporter_agent.generate_executive_summary(investigation_results)
                    
                    if summary.get('status') == 'SUCCESS':
                        st.session_state.analysis_results['results']['executive_summary'] = summary
                        st.success("✓ Executive report generated")
                        
                        # Show in reports tab
                        st.session_state.current_page = "reports"
                        st.rerun()
                    else:
                        st.error("Failed to generate executive report")
                else:
                    st.info("No investigation results available for report generation")
                    
            except Exception as e:
                st.error(f"Report generation failed: {e}")
    
    def run(self):
        """Main application run method"""
        # Render sidebar
        self.render_sidebar()
        
        # Render main content based on current page
        current_page = st.session_state.current_page
        
        if current_page == "dashboard":
            self.render_dashboard()
        elif current_page == "data_management":
            self.render_data_management()
        elif current_page == "variance_analysis":
            self.render_variance_analysis()
        elif current_page == "document_investigation":
            self.render_document_investigation()
        elif current_page == "reports":
            self.render_reports()
        elif current_page == "settings":
            self.render_settings()

# Run the app
if __name__ == "__main__":
    app = FPAApp()
    
    # Check if system is initialized
    if st.session_state.system_initialized:
        app.run()
    else:
        st.error("FP&A System failed to initialize. Please check your configuration.")
        
        if st.button("Retry Initialization"):
            try:
                app.initialize_system()
                st.session_state.system_initialized = True
                st.rerun()
            except Exception as e:
                st.error(f"Retry failed: {e}")
