# GitHub Deployment Guide

Complete instructions for setting up and running the FP&A Agent System from GitHub.

---

## 📌 For GitHub Users

This guide shows you exactly how to get the FP&A Agent running on your machine.

---

## Step-by-Step Setup & Run Commands

### **Step 1: Clone the Repository**

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/fpna-agent.git
cd fpna-agent
```

### **Step 2: Verify Prerequisites**

Before proceeding, ensure you have:
- ✅ Python 3.9 or higher
- ✅ LM Studio running with a model loaded
- ✅ Git installed

**Check Python version:**
```powershell
python --version
# Output should be: Python 3.9.x or higher
```

**Check LM Studio is running:**
```powershell
# In your browser, visit:
# http://192.168.153.1:1234
# Should show the LM Studio API interface
```

### **Step 3: Create Virtual Environment**

```powershell
# Create virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **Step 4: Install Dependencies**

```powershell
# Install required packages (this takes 2-5 minutes)
pip install -r requirements_minimal.txt

# Or for full features:
pip install -r requirements.txt
```

### **Step 5: (Optional) Configure LM Studio Connection**

If LM Studio is on a different IP/port, create `.env` file:

```powershell
# Create .env file
echo "LMSTUDIO_BASE_URL=http://YOUR_IP:1234" > .env
echo "MODEL_ID=your-model-name" >> .env

# Example:
# LMSTUDIO_BASE_URL=http://192.168.1.100:1234
# MODEL_ID=deepseek-r1-distill-qwen-7b
```

### **Step 6: Verify Installation**

```powershell
# Test LM Studio connection
python fpna-agent\main.py --test

# Expected output:
# ✓ LM Studio connection test: OK...
```

---

## 🚀 Running the Project

### **Option A: Command-Line Analysis (Fastest)**

```powershell
# Run complete analysis
python fpna-agent\main.py --analyze

# Run analysis for specific department
python fpna-agent\main.py --analyze Marketing

# View all generated reports
python fpna-agent\main.py --reports

# Show help with all options
python fpna-agent\main.py --help
```

### **Option B: Interactive Menu**

```powershell
# Start interactive mode
python fpna-agent\main.py --interactive

# Then select options:
# 1. Run complete analysis
# 2. Load documents
# 3. Test variance detection
# 4. Test RAG retrieval
# ... and more
```

### **Option C: Web UI (Streamlit)**

```powershell
# Start the web interface
streamlit run fpna-agent\app.py

# Open in browser: http://localhost:8501
# Navigate through Dashboard, Variance Analysis, Reports, etc.
```

---

## 📊 Viewing Results

### **After Running Analysis**

Reports are saved to: `fpna-agent/data/reports/`

```powershell
# List all reports
ls fpna-agent\data\reports\

# View specific report
cat fpna-agent\data\reports\executive_summary_*.txt

# Count reports by type
(ls fpna-agent\data\reports\*.json).Count  # JSON files
(ls fpna-agent\data\reports\*.txt).Count   # Text files
```

### **Expected Output Files**

```
data/reports/
├── budget_proposal_*.json          (Machine-readable proposals)
├── budget_proposal_*.txt           (Human-readable proposals)
├── executive_summary_*.txt         (Executive summary)
└── detailed_report_*.txt           (Detailed variance analysis)
```

---

## 🔄 Complete Copy-Paste Workflow

**Windows PowerShell:**
```powershell
# Step 1: Clone & Setup
git clone https://github.com/YOUR_USERNAME/fpna-agent.git
cd fpna-agent

# Step 2: Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Step 3: Install dependencies
pip install -r requirements_minimal.txt

# Step 4: Test connection
python fpna-agent\main.py --test

# Step 5: Run analysis
python fpna-agent\main.py --analyze

# Step 6: View reports
ls fpna-agent\data\reports\
cat fpna-agent\data\reports\executive_summary_*.txt

# Step 7: (Optional) Launch web UI
streamlit run fpna-agent\app.py
```

**macOS/Linux Bash:**
```bash
# Step 1: Clone & Setup
git clone https://github.com/YOUR_USERNAME/fpna-agent.git
cd fpna-agent

# Step 2: Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Step 3: Install dependencies
pip install -r requirements_minimal.txt

# Step 4: Test connection
python fpna-agent/main.py --test

# Step 5: Run analysis
python fpna-agent/main.py --analyze

# Step 6: View reports
ls fpna-agent/data/reports/
cat fpna-agent/data/reports/executive_summary_*.txt

# Step 7: (Optional) Launch web UI
streamlit run fpna-agent/app.py
```

---

## ⚡ Quick Commands Reference

| Purpose | Command |
|---------|---------|
| Test LM Studio | `python fpna-agent\main.py --test` |
| Run Analysis | `python fpna-agent\main.py --analyze` |
| Interactive Mode | `python fpna-agent\main.py --interactive` |
| View Reports | `python fpna-agent\main.py --reports` |
| Web UI | `streamlit run fpna-agent\app.py` |
| Help | `python fpna-agent\main.py --help` |
| Clear Reports | `python fpna-agent\main.py --clear-reports` |

---

## 📁 Directory Structure After First Run

```
fpna-agent/
├── venv/                           (Virtual environment - auto-created)
├── data/
│   ├── sample_financial_data.json  (Generated sample data)
│   ├── chroma_db/                  (Vector database - auto-created)
│   ├── cache/                      (Cache directory - auto-created)
│   ├── uploads/                    (Your documents here)
│   └── reports/                    (Generated reports ✓)
├── app.py
├── main.py
├── README.md
├── SETUP_AND_RUN.md
├── FIXES_APPLIED.md
├── GITHUB_DEPLOYMENT.md (this file)
└── ... (other files)
```

---

## 🆘 Troubleshooting

### **Problem: "LM Studio connection failed"**

```powershell
# Check LM Studio is running
# Visit: http://192.168.153.1:1234

# If different IP/port, update .env:
echo "LMSTUDIO_BASE_URL=http://YOUR_IP:1234" > .env

# Then test again
python fpna-agent\main.py --test
```

### **Problem: "Port 8501 already in use" (Streamlit)**

```powershell
# Use different port
streamlit run fpna-agent\app.py --server.port 8502

# Or kill existing process
Get-Process python | Stop-Process
```

### **Problem: "ModuleNotFoundError: No module named..."**

```powershell
# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements_minimal.txt --force-reinstall
```

### **Problem: Streamlit page shows errors**

```powershell
# Refresh the browser page (F5)
# If errors persist, restart Streamlit:
# 1. Press Ctrl+C in terminal
# 2. Run: streamlit run fpna-agent\app.py
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview and quick start |
| `SETUP_AND_RUN.md` | Detailed setup guide for all platforms |
| `FIXES_APPLIED.md` | Bug fixes and improvements made |
| `GITHUB_DEPLOYMENT.md` | This file - instructions for GitHub users |

---

## 🎯 Expected Results

After successfully running `python fpna-agent\main.py --analyze`:

✅ **Analysis Metrics:**
- Total accounts analyzed: 25
- Significant variances found: 11
- Investigations completed: 11
- Budget proposals generated: 11
- Processing time: ~3 minutes

✅ **Generated Files:**
- 11 budget proposal JSON files
- 11 budget proposal text files
- 1 executive summary
- 3+ detailed variance reports

✅ **Sample Output:**
```
📊 FP&A ANALYSIS RESULTS
================================================================================
📈 METRICS:
   • Total variances analyzed: 25
   • Significant variances found: 11
   • Investigations completed: 11
   • Budget proposals generated: 11
   • Processing time: 2m 56s

💰 BUDGET PROPOSALS (11):
   1. Marketing - Advertising Expense (Adjust: -$3,412)
   2. Sales - Software License (Adjust: +$8,424)
   ... (more proposals)

✅ Analysis complete! Check data/reports for detailed outputs.
```

---

## 🔐 Security Notes

- **Never commit** `.env` files to GitHub
- **Never share** LM Studio API credentials
- **Use .gitignore** to exclude sensitive data (already configured)
- **Keep LM Studio secure** behind firewall for production use

---

## ✅ Verification Checklist

Before considering setup complete:

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] LM Studio connection test passes
- [ ] First analysis ran successfully
- [ ] Reports generated in `data/reports/`
- [ ] Streamlit UI loads (optional)

---

## 🚀 Next Steps

1. ✅ Complete the setup above
2. ✅ Run your first analysis
3. ✅ Review generated reports
4. ✅ Customize settings in `.env` if needed
5. ✅ Explore web UI for interactive analysis
6. ✅ Use for your financial data

---

## 📞 Getting Help

1. **Check documentation:**
   - [README.md](README.md) - Overview
   - [SETUP_AND_RUN.md](SETUP_AND_RUN.md) - Detailed setup
   - [FIXES_APPLIED.md](FIXES_APPLIED.md) - Known issues

2. **Verify prerequisites:**
   - Python version: `python --version`
   - LM Studio running: `http://192.168.153.1:1234`
   - Connection test: `python fpna-agent\main.py --test`

3. **Common issues:**
   - See Troubleshooting section above
   - Check your `.env` configuration
   - Ensure virtual environment is activated

---

**Last Updated**: 2026-06-22  
**Version**: 1.0  
**Status**: ✅ Production Ready
