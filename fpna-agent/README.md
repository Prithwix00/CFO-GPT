# FP&A Agent System

An Agentic RAG-powered Financial Planning & Analysis system that automates variance detection, investigation, and reporting while keeping humans in control.

## ⚡ Quick Start

### Option 1: Command-Line (Fastest)
```powershell
# Setup (one-time)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements_minimal.txt

# Run analysis
python fpna-agent\main.py --analyze

# View reports
ls fpna-agent\data\reports\
```

### Option 2: Web UI (Recommended for Exploration)
```powershell
# Setup (one-time)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements_minimal.txt

# Start Streamlit
streamlit run fpna-agent\app.py
# Then open http://localhost:8501
```

**For detailed instructions**, see [SETUP_AND_RUN.md](SETUP_AND_RUN.md)

---

## 📋 Features

- **Automatic Variance Detection**: Identifies significant budget vs actual variances
- **Agentic RAG Investigation**: Retrieves and analyzes invoices, contracts, and approvals
- **Root Cause Analysis**: Identifies underlying causes of variances
- **Automated Reporting**: Generates executive summaries and budget proposals
- **Human-in-the-Loop**: No autonomous approvals - human validation required
- **Streamlit UI**: User-friendly web interface for exploration
- **CLI Interface**: Command-line tools for automation and scripting

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│          FP&A Agent System Flow                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Financial Data ──┐                                 │
│  (Budget/Actual) ├─→ [Monitor Agent]                │
│                  │   └→ Variance Detection          │
│                  │                                  │
│  Supporting     ──┐                                 │
│  Docs           ├─→ [RAG System]                    │
│  (Invoices)     │   ├→ Document Loading             │
│                 │   ├→ Vector Store (Chroma)        │
│                 │   └→ Similarity Search            │
│                 │                                  │
│                 ├─→ [Investigator Agent]            │
│                 │   └→ Root Cause Analysis          │
│                 │                                  │
│                 └─→ [Reporter Agent]                │
│                     ├→ Budget Proposals             │
│                     ├→ Recommendations              │
│                     └→ Executive Summary            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Commands Reference

### Analysis & Reports
```powershell
python fpna-agent\main.py --analyze                    # Run full analysis
python fpna-agent\main.py --analyze Marketing          # Analyze specific dept
python fpna-agent\main.py --reports                    # List all reports
python fpna-agent\main.py --clear-reports              # Clear report directory
```

### Testing & Debugging
```powershell
python fpna-agent\main.py --test                       # Test LM Studio connection
python fpna-agent\main.py --interactive                # Interactive menu
python fpna-agent\main.py --help                       # Show help
```

### Web Interface
```powershell
streamlit run fpna-agent\app.py                        # Start web UI
streamlit run fpna-agent\app.py --server.port 8502     # Use custom port
```

---

## 📚 Documentation

- **[SETUP_AND_RUN.md](SETUP_AND_RUN.md)** - Complete setup and run guide with step-by-step instructions
- **[FIXES_APPLIED.md](FIXES_APPLIED.md)** - Bug fixes and improvements made to the system
- **README.md** - This file

---

## ⚙️ Prerequisites

- **Python 3.9+**
- **LM Studio** (running locally, default: `http://192.168.153.1:1234`)
- **Supported OS**: Windows 10+, macOS, Linux

### LM Studio Setup
1. Download [LM Studio](https://lmstudio.ai/)
2. Load a model (e.g., `deepseek-r1-distill-qwen-7b`)
3. Start the server (default: `http://192.168.153.1:1234`)
4. Verify it's running by visiting the URL in your browser

---

## 📦 Project Structure

```
fpna-agent/
├── app.py                              # Streamlit web UI
├── main.py                             # CLI entry point
├── SETUP_AND_RUN.md                    # Setup guide (START HERE!)
├── FIXES_APPLIED.md                    # Bug fixes documentation
├── README.md                           # This file
├── requirements_minimal.txt            # Minimal dependencies
├── requirements.txt                    # Full dependencies
├── config/
│   ├── __init__.py
│   └── settings.py                     # Configuration
├── src/
│   ├── agents/                         # AI agents
│   │   ├── base_agent.py
│   │   ├── monitor_agent.py
│   │   ├── investigator.py
│   │   └── reporter_agent.py
│   ├── rag/                            # RAG system
│   │   ├── loader.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   ├── analysis/                       # Analysis engines
│   │   ├── variance_engine.py
│   │   └── trend_analyzer.py
│   ├── workflows/                      # Main workflow
│   │   └── fpa_workflow.py
│   └── utils/                          # Utilities
│       └── data_loader.py
├── data/
│   ├── sample_financial_data.json
│   ├── uploads/                        # Document uploads
│   ├── reports/                        # Generated reports
│   ├── chroma_db/                      # Vector store
│   └── cache/                          # Cache directory
└── test_*.py                           # Test files
```

---

## 📊 Output Examples

The system generates comprehensive reports:

### Budget Proposal (JSON)
```json
{
  "department": "Marketing",
  "account": "Advertising Expense",
  "current_budget": 42226.42,
  "actual_spend": 35402.42,
  "variance_amount": -6824.00,
  "proposed_budget": 38814.42,
  "adjustment_amount": 3412.00,
  "justification": "Based on 16.2% underspend...",
  "confidence": 35.0
}
```

### Executive Summary
- Department-wise variance analysis
- Root cause findings
- Key recommendations
- Risk assessment

### Detailed Reports
- Per-variance investigation results
- Evidence and supporting documents
- Confidence metrics
- Action items

---

## 🚀 Example Workflow

```powershell
# 1. Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements_minimal.txt

# 2. Run analysis
python fpna-agent\main.py --analyze

# 3. View results
dir fpna-agent\data\reports\

# 4. (Optional) Launch web UI
streamlit run fpna-agent\app.py
```

---

## ✅ What You'll Get

After running analysis:
- ✅ 11 budget proposals (JSON + text format)
- ✅ 1 executive summary
- ✅ Multiple detailed variance reports
- ✅ Root cause analysis for each variance
- ✅ Actionable recommendations
- ✅ Processing metrics and confidence levels

---

## 🐛 Known Issues

See [FIXES_APPLIED.md](FIXES_APPLIED.md) for details on known issues and workarounds.

### Troubleshooting
For common issues and solutions, see the **Troubleshooting** section in [SETUP_AND_RUN.md](SETUP_AND_RUN.md)

---

## 📝 License

[Add your license here - MIT, Apache 2.0, etc.]

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

---

## 📞 Support

For issues, questions, or suggestions:
- Check [SETUP_AND_RUN.md](SETUP_AND_RUN.md) for detailed troubleshooting
- Review [FIXES_APPLIED.md](FIXES_APPLIED.md) for known issues
- Open an issue on GitHub

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-06-22  
**Version**: 1.0
