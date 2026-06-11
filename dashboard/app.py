import streamlit as st

import os

# Auto-generate data if not exists
if not os.path.exists("data/lakehouse/gold/daily_costs.parquet"):
    os.system("python ingestion/mock_generator.py")
    os.system("python lakehouse/bronze_writer.py")
    os.system("python lakehouse/silver_transformer.py")
    os.system("python lakehouse/gold_aggregator.py")
    os.system("python agent/nodes/anomaly_detector.py")
    os.system("python agent/nodes/root_cause_analyst.py")

st.set_page_config(page_title="FinOps Intelligence", layout="wide")

st.title("💰 FinOps Intelligence Dashboard")

st.markdown("""
Welcome to your FinOps AI system  
- 📈 Cost trends  
- 🚨 Anomaly detection  
- 🧠 Root cause insights  
""")

st.sidebar.success("Select a page above 👆")