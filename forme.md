# Step 1: Navigate to project
cd fpna-agent

# Step 2: Create virtual environment
python -m venv venv

# Step 3: Activate it
.\venv\Scripts\Activate.ps1

# Step 4: Install dependencies (takes 2-5 min)
pip install -r requirements_minimal.txt

# Step 5: Test LM Studio connection
python fpna-agent\main.py --test

# Step 6: Start Streamlit web UI
streamlit run fpna-agent\app.py




cd fpna-agent
.\venv\Scripts\Activate.ps1
streamlit run app.py