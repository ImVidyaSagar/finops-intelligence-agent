import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DAILY_PATH = "data/lakehouse/gold/daily_costs.parquet"
ANOMALY_PATH = "data/lakehouse/gold/anomalies_detected.parquet"

st.title("📈 Cost Overview")

daily = pd.read_parquet(DAILY_PATH)
anomalies = pd.read_parquet(ANOMALY_PATH)

# Normalize dates
daily['usage_date'] = pd.to_datetime(daily['usage_date'])
anomalies['usage_date'] = pd.to_datetime(anomalies['usage_date'])

# Aggregate anomaly points
anomaly_points = anomalies.groupby('usage_date')['service_cost'].sum().reset_index()

fig = go.Figure()

# Line chart
fig.add_trace(go.Scatter(
    x=daily['usage_date'],
    y=daily['total_cost'],
    mode='lines',
    name='Total Cost'
))

# Anomaly markers
fig.add_trace(go.Scatter(
    x=anomaly_points['usage_date'],
    y=anomaly_points['service_cost'],
    mode='markers',
    name='Anomalies',
    marker=dict(size=10, symbol='circle')
))

fig.update_layout(
    title="Daily Cost with Anomalies",
    xaxis_title="Date",
    yaxis_title="Cost ($)"
)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Cost", f"${daily['total_cost'].sum():,.0f}")

with col2:
    st.metric("Avg Daily", f"${daily['total_cost'].mean():,.0f}")

with col3:
    st.metric("Anomalies", len(anomalies))

st.plotly_chart(fig, use_container_width=True)