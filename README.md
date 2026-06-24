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
