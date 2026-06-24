# FP&A Agent System - Setup & Run Guide

Complete step-by-step instructions to set up and run the FP&A Agent system from scratch.

## Prerequisites

- **Windows 10/11** (or Linux/Mac with PowerShell/Bash)
- **Python 3.9+** installed
- **LM Studio** running locally with a model loaded (default: `http://192.168.153.1:1234`)
- **Git** (for cloning the repository)

---

## 1. Clone or Download the Project

```powershell
# Clone the repository (if using Git)
git clone <repository-url>
cd fpna-agent

# Or extract the ZIP file and navigate to the directory
```

---

## 2. Create and Activate Virtual Environment

### On Windows (PowerShell):

```powershell
# Navigate to project root
cd fpna-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### On macOS/Linux (Bash):

```bash
cd fpna-agent
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```powershell
# Install minimal dependencies (recommended for first-time setup)
pip install -r requirements_minimal.txt

# OR install full dependencies (if you need all features)
pip install -r requirements.txt
```

**Note**: Installation may take 2-5 minutes as it downloads LLM libraries and Chroma DB.

---

## 4. Configure LM Studio Connection

### Option A: Default Configuration (Recommended)
If LM Studio is running on `http://192.168.153.1:1234` with model `deepseek-r1-distill-qwen-7b`, skip to the next step.

### Option B: Custom Configuration
Create or update `.env` file in the project root:

```
LMSTUDIO_BASE_URL=http://your-ip:1234
MODEL_ID=your-model-name
VARIANCE_THRESHOLD=0.10
SIGNIFICANT_AMOUNT=10000.0
MAX_TOKENS=4096
REQUEST_TIMEOUT=120
```

---

## 5. Run the FP&A Agent

### Option 1: Command-Line Analysis (Fastest)

```powershell
# Run complete analysis with default settings
python fpna-agent\main.py --analyze

# Run analysis for specific department
python fpna-agent\main.py --analyze Marketing

# Show all saved reports
python fpna-agent\main.py --reports

# Clear report directory (with confirmation)
python fpna-agent\main.py --clear-reports

# Test LM Studio connection
python fpna-agent\main.py --test

# Show help with all available commands
python fpna-agent\main.py --help
```

### Option 2: Interactive CLI Mode

```powershell
# Start interactive menu
python fpna-agent\main.py --interactive
```

Then select options:
1. Run complete analysis
2. Load documents only
3. Test variance detection
4. Test RAG retrieval
5. Generate sample data
6. Check report directory
7. Test agent connections
8. Clear report directory
9. View system settings
10. Exit

### Option 3: Streamlit Web UI (Recommended for Exploration)

```powershell
# Start Streamlit web interface
streamlit run fpna-agent\app.py

# Custom port (if 8501 is busy)
streamlit run fpna-agent\app.py --server.port 8502

# Headless mode (background server)
python -m streamlit run fpna-agent\app.py --server.port 8501 --server.headless true
```

Then open your browser to: **http://localhost:8501**

---

## 6. View Results

### Report Files Location
All reports are saved to: `fpna-agent/data/reports/`

**Report types:**
- `budget_proposal_*.json` - Machine-readable budget proposals
- `budget_proposal_*.txt` - Human-readable budget proposals
- `executive_summary_*.txt` - Executive summary report
- `detailed_report_*.txt` - Detailed analysis for each variance

### Sample Output Files
Example reports from a recent run:
```
data/reports/
├── budget_proposal_Marketing_Advertising_Expense_20260622_120956.json
├── budget_proposal_Marketing_Advertising_Expense_20260622_120956.txt
├── executive_summary_20260622_121033.txt
├── detailed_report_Marketing_Advertising_Expense_20260622_121039.txt
└── ... (more reports)
```

### View Report Files
```powershell
# List all reports
ls fpna-agent\data\reports\

# Open a specific report
cat fpna-agent\data\reports\executive_summary_*.txt

# Count files by type
(ls fpna-agent\data\reports\*.json).Count  # JSON files
(ls fpna-agent\data\reports\*.txt).Count   # Text files
```

---

## 7. (Optional) Run Tests

```powershell
# Run all tests
pytest -v

# Run specific test file
pytest fpna-agent\test_lm_connection.py -v

# Run tests with coverage
pytest --cov=fpna-agent fpna-agent\
```

---

## 8. Troubleshooting

### Issue: "LM Studio connection failed"
**Solution:**
- Verify LM Studio is running: http://192.168.153.1:1234
- Check model is loaded in LM Studio
- Update `.env` if using different IP/port

### Issue: "ModuleNotFoundError" when importing packages
**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements_minimal.txt --force-reinstall
```

### Issue: "Port 8501 already in use" (Streamlit)
**Solution:**
```powershell
# Use different port
streamlit run fpna-agent\app.py --server.port 8502

# Or kill the existing process
# (Windows) Get-Process python | Stop-Process
# (Mac/Linux) pkill -f streamlit
```

### Issue: ChromaDB telemetry errors in logs
**Solution:** These are harmless warnings. The system works fine. To suppress them:
```powershell
$env:ANONYMIZED_TELEMETRY="false"
$env:POSTHOG_DISABLED="true"
python fpna-agent\main.py --analyze
```

---

## 9. Quick Start Summary (Copy-Paste Commands)

### Windows PowerShell:
```powershell
# 1. Setup (one-time)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements_minimal.txt

# 2. Run analysis
python fpna-agent\main.py --analyze

# 3. View reports
ls fpna-agent\data\reports\

# 4. Start web UI (optional)
streamlit run fpna-agent\app.py
```

### macOS/Linux Bash:
```bash
# 1. Setup (one-time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_minimal.txt

# 2. Run analysis
python fpna-agent/main.py --analyze

# 3. View reports
ls fpna-agent/data/reports/

# 4. Start web UI (optional)
streamlit run fpna-agent/app.py
```

---

## 10. Project Structure

```
fpna-agent/
├── app.py                          # Streamlit web UI
├── main.py                         # CLI entry point
├── config/
│   ├── __init__.py
│   └── settings.py                 # Configuration & settings
├── src/
│   ├── agents/
│   │   ├── base_agent.py           # Base agent class
│   │   ├── monitor_agent.py        # Variance detection
│   │   ├── investigator.py         # Root cause analysis
│   │   └── reporter_agent.py       # Report generation
│   ├── rag/
│   │   ├── loader.py               # Document loading
│   │   ├── vector_store.py         # Chroma DB integration
│   │   └── retriever.py            # RAG retrieval
│   ├── analysis/
│   │   ├── variance_engine.py      # Variance calculations
│   │   └── trend_analyzer.py       # Trend analysis
│   ├── workflows/
│   │   └── fpa_workflow.py         # Main workflow orchestration
│   └── utils/
│       └── data_loader.py          # Data loading utilities
├── data/
│   ├── sample_financial_data.json  # Sample data
│   ├── uploads/                    # Document uploads
│   ├── reports/                    # Generated reports
│   ├── chroma_db/                  # Vector store
│   └── cache/                      # Cache directory
├── requirements_minimal.txt        # Minimal dependencies
├── requirements.txt                # Full dependencies
├── README.md                       # Project overview
└── SETUP_AND_RUN.md               # This file
```

---

## 11. System Capabilities

The system can:
- ✅ Analyze 25+ accounts for budget variances
- ✅ Identify 10+ significant variances per analysis
- ✅ Generate root cause analysis for each variance
- ✅ Create budget adjustment proposals
- ✅ Generate executive summaries
- ✅ Support multi-department analysis
- ✅ Process documents for context (invoices, contracts, etc.)
- ✅ Provide human-in-the-loop approval workflow

---

## 12. Performance Expectations

| Operation | Time |
|-----------|------|
| System initialization | 5-10 sec |
| Variance detection | 10 sec |
| Investigation per variance | 10 sec × N variances |
| Report generation | 5 sec per report |
| **Total analysis (11 variances)** | **~3 minutes** |

---

## 13. For GitHub

When publishing to GitHub, include:

1. ✅ This `SETUP_AND_RUN.md` file
2. ✅ Updated `README.md` with quick start
3. ✅ `.gitignore` (exclude `venv/`, `data/`, `.env`)
4. ✅ `requirements_minimal.txt` and `requirements.txt`
5. ✅ `LICENSE` file
6. ✅ Sample data in `data/sample_financial_data.json`

### Example `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
data/chroma_db/
data/cache/
data/uploads/*
data/reports/*
.DS_Store
*.log
```

---

## Support & Troubleshooting

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review logs in `data/fpa_system.log`
3. Run `python fpna-agent\main.py --test` to verify connections
4. Check LM Studio is running with a model loaded

---

**Last Updated**: 2026-06-22  
**Version**: 1.0  
**Status**: ✅ Working
