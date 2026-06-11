# 💰 FinOps Intelligence Agent

An end-to-end data engineering + analytics system that detects, explains, and answers cloud cost anomalies.

---

## 🚀 Features

* 🏗️ Medallion Architecture (Bronze → Silver → Gold)
* 📊 Cost trend analytics
* 🚨 Anomaly detection using statistical baselines (Z-score)
* 📈 Precision: ~80% (validated against ground truth)
* 🧠 Root cause analysis (region + resource level)
* 🤖 AI agent for natural language queries
* 📊 Streamlit dashboard

---

## 🏛️ Architecture

```
Raw Data → Bronze → Silver → Gold → Anomaly Detection → Root Cause → AI Agent → Dashboard
```

---

## 📊 Sample Insights

* Azure OpenAI Service spike driven by GPU inference in Australia East
* Kubernetes cost spike due to CPU usage in Central India
* Blob Storage anomaly from storage surge in Southeast Asia

---

## 🛠️ Tech Stack

* Python, Pandas, DuckDB
* Delta Lake
* Streamlit + Plotly
* LangGraph (AI agent)
* PyTest (validation)

---

## ▶️ How to Run

```bash
pip install -r requirements.txt

# Generate mock data
python ingestion/mock_generator.py

# Run pipeline
python lakehouse/bronze_writer.py
python lakehouse/silver_transformer.py
python lakehouse/gold_aggregator.py

# Detect anomalies
python agent/nodes/anomaly_detector.py

# Root cause analysis
python agent/nodes/root_cause_analyst.py

# Run dashboard
python -m streamlit run dashboard/app.py
```

---

## 🧠 Key Learnings

* Built production-style data pipelines
* Improved anomaly detection using statistical modeling
* Balanced precision vs recall using business thresholds
* Designed explainable AI system for FinOps

---

## 📌 Author

Vidya Sagar

