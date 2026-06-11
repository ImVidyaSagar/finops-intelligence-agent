import streamlit as st
import pandas as pd

ANOMALY_PATH = "data/lakehouse/gold/anomalies_detected.parquet"
ROOT_PATH = "data/lakehouse/gold/anomaly_root_causes.parquet"

st.title("🚨 Anomaly Detection")

anomalies = pd.read_parquet(ANOMALY_PATH)
root = pd.read_parquet(ROOT_PATH)

# Normalize dates
anomalies['usage_date'] = pd.to_datetime(anomalies['usage_date']).dt.date
root['usage_date'] = pd.to_datetime(root['usage_date']).dt.date

df = anomalies.merge(root, on=["usage_date", "service_name"], how="left")

st.dataframe(df.sort_values("usage_date", ascending=False))
st.subheader("🧠 Key Insights")

for _, row in df.head(5).iterrows():
    st.markdown(f"""
🔴 **{row['service_name']} spike**  
📅 Date: {row['usage_date']}  
💰 Cost: ${row['service_cost']:.0f} ({row['deviation_ratio']:.1f}x baseline)  
⚙️ Cause: {row.get('top_chip', 'N/A')}  
🌍 Region: {row.get('top_region', 'N/A')}  
""")
