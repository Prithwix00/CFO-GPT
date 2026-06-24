# Deploy FP&A Agent with Streamlit UI - Step-by-Step Guide

Complete commands to get the web UI running.

---

## ⚡ Quick Deploy (Copy-Paste)

### **Windows PowerShell - First Time Setup**

```powershell
# Navigate to project folder
cd fpna-agent

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If execution policy error, run this first:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# Install packages (takes 2-5 minutes)
pip install -r requirements_minimal.txt

# Test LM Studio connection
python fpna-agent\main.py --test

# Launch Streamlit web UI
streamlit run fpna-agent\app.py
```

**Browser will open automatically to:** `http://localhost:8501`

---

### **macOS/Linux - First Time Setup**

```bash
# Navigate to project folder
cd fpna-agent

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install packages (takes 2-5 minutes)
pip install -r requirements_minimal.txt

# Test LM Studio connection
python fpna-agent/main.py --test

# Launch Streamlit web UI
streamlit run fpna-agent/app.py
```

**Browser will open automatically to:** `http://localhost:8501`

---

## 🔄 Subsequent Runs (After First Setup)

### **Windows PowerShell**

```powershell
cd fpna-agent
.\venv\Scripts\Activate.ps1
streamlit run fpna-agent\app.py
```

### **macOS/Linux**

```bash
cd fpna-agent
source venv/bin/activate
streamlit run fpna-agent/app.py
```

---

## 📊 Using the Web UI

### **Dashboard** (Landing Page)
1. ✅ View system status
2. ✅ Run quick actions (Refresh, Run Analysis)
3. ✅ See recent metrics
4. ✅ View top variances

### **Data Management** Tab
- Upload financial data (CSV/JSON)
- Generate sample data
- Upload supporting documents (PDF, invoices, etc.)
- Manage documents

### **Variance Analysis** Tab
- Set variance thresholds
- Configure significance amount
- Select department filter
- Run analysis
- View charts and tables

### **Document Investigation** Tab
- Search documents by query
- Select variance to investigate
- View root cause analysis
- See recommendations

### **Reports & Proposals** Tab
- View executive summary
- Download budget proposals
- View detailed reports
- Export to file

### **Settings** Tab
- Configure LM Studio connection
- Set agent parameters
- Adjust financial thresholds
- Manage vector store

---

## 🎯 Complete Workflow in UI

### **Step 1: Load Sample Data**
1. Go to **Data Management** → **Generate Sample**
2. Click "Generate Sample Financial Data"
3. ✅ 25 sample records created

### **Step 2: Run Analysis**
1. Go to **Dashboard** or **Variance Analysis**
2. Click "Run Variance Analysis" button
3. ⏳ Wait ~3 minutes for completion
4. ✅ 11 significant variances found

### **Step 3: Investigate Variances**
1. Go to **Document Investigation** → **Investigate Variance**
2. Select a variance from dropdown
3. Click "Investigate Variance"
4. ✅ View root cause analysis & recommendations

### **Step 4: Review Proposals**
1. Go to **Reports & Proposals** → **Budget Proposals**
2. Expand each proposal
3. View justification & confidence level
4. Download as text file

### **Step 5: Export Reports**
1. Go to **Reports & Proposals** → **Detailed Reports**
2. Download Executive Summary
3. Download Variance Report
4. ✅ Files saved to your computer

---

## 🔧 Advanced Options

### **Custom Port (if 8501 is busy)**

```powershell
streamlit run fpna-agent\app.py --server.port 8502
# Open: http://localhost:8502
```

### **Headless Mode (Background Server)**

```powershell
python -m streamlit run fpna-agent\app.py --server.port 8501 --server.headless true
# Browser won't open automatically
# Visit: http://localhost:8501
```

### **Wide Layout**

```powershell
streamlit run fpna-agent\app.py --logger.level=error --client.showErrorDetails=false
```

### **Clear Cache (if UI behaves strangely)**

```powershell
# Delete cache directory
rmdir /s C:\Users\YOUR_USER\AppData\Local\streamlit\cache

# Then restart
streamlit run fpna-agent\app.py
```

---

## 🚨 Troubleshooting

### **Port 8501 Already in Use**

**Option 1: Use different port**
```powershell
streamlit run fpna-agent\app.py --server.port 8502
```

**Option 2: Kill existing process**
```powershell
# PowerShell
Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force

# Or find exact process:
Get-Process python
Stop-Process -Id <PID> -Force
```

### **LM Studio Connection Failed**

```powershell
# 1. Check LM Studio is running
# Open browser: http://192.168.153.1:1234

# 2. If different IP, add to .env
echo "LMSTUDIO_BASE_URL=http://YOUR_IP:1234" > .env

# 3. Test connection
python fpna-agent\main.py --test

# 4. Restart Streamlit
streamlit run fpna-agent\app.py
```

### **Virtual Environment Not Activating**

```powershell
# If venv doesn't activate, recreate it:
rmdir venv /s /q
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements_minimal.txt
```

### **Missing Packages Error**

```powershell
# Reinstall all packages
pip install -r requirements_minimal.txt --force-reinstall --no-cache-dir
```

### **Streamlit Hangs or Crashes**

```powershell
# 1. Stop with Ctrl+C
# 2. Clear cache
streamlit cache clear

# 3. Restart
streamlit run fpna-agent\app.py
```

---

## 📱 Accessing from Another Machine

### **From Another Computer on Same Network**

Get your IP address:

**Windows:**
```powershell
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.x.x)
```

**macOS/Linux:**
```bash
ifconfig
# Look for inet address (e.g., 192.168.x.x)
```

Then visit from another machine:
```
http://YOUR_IP:8501
```

### **Port Forwarding (For External Access)**

This requires router configuration. Basic steps:

1. Find your external IP: `https://www.whatismyip.com/`
2. Configure port forwarding on router (8501 → your machine)
3. Access from anywhere: `http://YOUR_EXTERNAL_IP:8501`

⚠️ **Security Warning**: For production, use proper authentication!

---

## 🐳 Docker Deployment (Optional)

### **Create Dockerfile**

Create file `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_minimal.txt .
RUN pip install --no-cache-dir -r requirements_minimal.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "fpna-agent/app.py"]
```

### **Build and Run Docker Image**

```bash
# Build image
docker build -t fpna-agent:latest .

# Run container
docker run -p 8501:8501 fpna-agent:latest

# Visit: http://localhost:8501
```

---

## 🌐 Cloud Deployment (Streamlit Cloud)

### **Deploy to Streamlit Cloud (Free)**

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your GitHub repo and `fpna-agent\app.py`
5. ✅ Live in 2 minutes!

**Note**: Requires LM Studio accessible from cloud or API endpoint.

---

## 📊 UI Features Overview

| Feature | Location | Purpose |
|---------|----------|---------|
| **Dashboard** | Home | Overview & quick actions |
| **Data Upload** | Data Management | Upload financial data |
| **Sample Data** | Data Management | Generate test data |
| **Document Upload** | Data Management | Upload invoices/contracts |
| **Variance Analysis** | Variance Analysis | Run & configure analysis |
| **Document Search** | Investigation | Search documents |
| **Investigate** | Investigation | Deep-dive analysis |
| **Executive Summary** | Reports | High-level overview |
| **Budget Proposals** | Reports | Adjustment proposals |
| **Settings** | Settings | Configure system |

---

## 🎬 Expected Behavior

### **First Load**
```
✓ Initializing FP&A System...
✓ FP&A System initialized successfully
  - Dashboard appears
  - Sidebar shows System Ready ✅
```

### **After Loading Data**
```
✓ System Ready
✓ Documents Loaded: X
✓ Dashboard metrics update
```

### **During Analysis**
```
⏳ Running variance analysis...
  - Progress shown
  - Results appear in 3-5 minutes
```

### **After Analysis**
```
✓ Dashboard shows:
  - Total variances analyzed
  - Significant variances found
  - Investigations completed
  - Processing time
```

---

## 💾 File Locations

All data saved locally in: `fpna-agent/data/`

```
fpna-agent/data/
├── sample_financial_data.json      (Generated data)
├── uploads/                        (Your uploaded documents)
├── reports/                        (Generated proposals & reports)
├── chroma_db/                      (Vector database)
└── cache/                          (Cache files)
```

---

## 🔐 Security Notes for Deployment

### **For Local Use (Recommended)**
- ✅ Access from localhost only
- ✅ No authentication needed
- ✅ LM Studio on same network

### **For Shared Access**
- ⚠️ Add password authentication
- ⚠️ Use HTTPS/SSL
- ⚠️ Restrict IP ranges
- ⚠️ Keep LM Studio behind firewall

### **For Production**
- ⚠️ Use proper authentication system
- ⚠️ Encrypt data in transit (HTTPS)
- ⚠️ Implement access control
- ⚠️ Use managed LM Studio API
- ⚠️ Set up monitoring/logging

---

## 📝 Configuration in UI

### **Via Settings Tab**

1. **LM Studio URL**: Configure API endpoint
2. **Model ID**: Select which model to use
3. **Temperature**: Control output randomness (0.0-1.0)
4. **Max Tokens**: Limit response length
5. **Variance Threshold**: Set % threshold (1-50%)
6. **Significant Amount**: Set $ threshold ($1k-$100k)

All changes take effect immediately!

---

## ✅ Verification Checklist

Before considering deployment complete:

- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] LM Studio connection test passes
- [ ] Streamlit starts without errors
- [ ] Dashboard page loads
- [ ] Can generate sample data
- [ ] Can run analysis
- [ ] Reports save to data/reports/
- [ ] Web UI is responsive
- [ ] All pages load correctly

---

## 🚀 Quick Reference Card

```
FIRST TIME:
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements_minimal.txt
  streamlit run fpna-agent\app.py

EVERY OTHER TIME:
  .\venv\Scripts\Activate.ps1
  streamlit run fpna-agent\app.py

ACCESS:
  http://localhost:8501

STOP:
  Ctrl + C in terminal

LOGS:
  Check terminal output
```

---

## 📞 Support

- **Can't connect?** Check LM Studio is running
- **Port busy?** Use `--server.port 8502`
- **Slow response?** Check LM Studio logs
- **Want CLI?** Run `python fpna-agent\main.py --analyze`
- **Need help?** See SETUP_AND_RUN.md

---

**Status**: ✅ Ready to Deploy  
**Last Updated**: 2026-06-22  
**Version**: 1.0
