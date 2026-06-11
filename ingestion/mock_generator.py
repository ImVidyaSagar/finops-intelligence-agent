"""
mock_generator.py
Generates realistic Azure cloud cost data for local development and public demo.
Produces 6 months of daily cost records with injected anomalies.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

SEED = 42
NUM_DAYS = 180          # 6 months
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "mock"

random.seed(SEED)
np.random.seed(SEED)

# ── Azure services with realistic base costs (USD/day) and chip family ────────

SERVICES = [
    {"name": "Azure Virtual Machines",      "base": 420,  "chip": "cpu_general",   "category": "Compute"},
    {"name": "Azure Kubernetes Service",     "base": 310,  "chip": "cpu_general",   "category": "Compute"},
    {"name": "Azure Machine Learning",       "base": 580,  "chip": "gpu_training",  "category": "AI/ML"},
    {"name": "Azure OpenAI Service",         "base": 260,  "chip": "gpu_inference", "category": "AI/ML"},
    {"name": "Azure Databricks",             "base": 390,  "chip": "cpu_general",   "category": "Analytics"},
    {"name": "Azure Synapse Analytics",      "base": 210,  "chip": "cpu_general",   "category": "Analytics"},
    {"name": "Azure Data Factory",           "base": 95,   "chip": "cpu_general",   "category": "Integration"},
    {"name": "Azure Blob Storage",           "base": 140,  "chip": "storage",       "category": "Storage"},
    {"name": "Azure Data Lake Storage Gen2", "base": 175,  "chip": "storage",       "category": "Storage"},
    {"name": "Azure SQL Database",           "base": 185,  "chip": "cpu_general",   "category": "Database"},
    {"name": "Azure Cosmos DB",              "base": 230,  "chip": "cpu_general",   "category": "Database"},
    {"name": "Azure Stream Analytics",       "base": 120,  "chip": "cpu_general",   "category": "Integration"},
    {"name": "Azure Functions",              "base": 45,   "chip": "cpu_serverless","category": "Compute"},
    {"name": "Azure Monitor",                "base": 80,   "chip": "cpu_general",   "category": "Management"},
    {"name": "Azure Purview",                "base": 60,   "chip": "cpu_general",   "category": "Governance"},
]

REGIONS = [
    "East US", "West Europe", "Southeast Asia",
    "Central India", "UK South", "Australia East"
]

ENVIRONMENTS = ["production", "staging", "development"]
ENV_WEIGHTS  = [0.65, 0.22, 0.13]          # prod dominates cost

COST_CENTRES = ["data-platform", "ml-engineering", "cloud-infra", "finops", "analytics"]

# ── Anomaly injection config ──────────────────────────────────────────────────
# Each tuple: (day_offset_from_start, service_name, multiplier, reason)

ANOMALIES = [
    (30,  "Azure Machine Learning",       3.8, "GPU cluster left running overnight — training job not terminated"),
    (55,  "Azure Blob Storage",           4.2, "Accidental public container — massive egress from data leak"),
    (80,  "Azure Kubernetes Service",     2.9, "HPA misconfiguration — pods scaled to max on low-traffic day"),
    (110, "Azure OpenAI Service",         5.1, "Runaway API calls from misconfigured retry logic in prod"),
    (140, "Azure Data Factory",           3.3, "Pipeline trigger duplicated — all jobs ran 4x on same day"),
    (160, "Azure Databricks",             2.6, "All-purpose cluster used instead of job cluster for batch job"),
]

# ── Generator ─────────────────────────────────────────────────────────────────

def generate_cost_records() -> pd.DataFrame:
    start_date = datetime.today() - timedelta(days=NUM_DAYS)
    records = []

    anomaly_index = {(a[0], a[1]): (a[2], a[3]) for a in ANOMALIES}

    for day_offset in range(NUM_DAYS):
        date = start_date + timedelta(days=day_offset)

        # Weekly pattern: weekends ~30% cheaper (less dev activity)
        weekday_factor = 0.70 if date.weekday() >= 5 else 1.0

        # Gradual upward trend simulating org growth (~15% over 6 months)
        growth_factor = 1.0 + (day_offset / NUM_DAYS) * 0.15

        for svc in SERVICES:
            for region in random.sample(REGIONS, k=random.randint(2, 4)):
                env = random.choices(ENVIRONMENTS, weights=ENV_WEIGHTS)[0]
                cost_centre = random.choice(COST_CENTRES)

                # Base cost with noise
                base = svc["base"] * weekday_factor * growth_factor
                noise = np.random.normal(0, base * 0.08)   # ±8% daily variance
                cost = max(0.0, base + noise)

                # Apply anomaly if this day+service matches
                anomaly_key = (day_offset, svc["name"])
                anomaly_flag = False
                anomaly_reason = None

                if anomaly_key in anomaly_index:
                    multiplier, reason = anomaly_index[anomaly_key]
                    cost *= multiplier
                    anomaly_flag = True
                    anomaly_reason = reason

                records.append({
                    "date":             date.strftime("%Y-%m-%d"),
                    "service_name":     svc["name"],
                    "category":         svc["category"],
                    "chip_family":      svc["chip"],
                    "region":           region,
                    "environment":      env,
                    "cost_centre":      cost_centre,
                    "cost_usd":         round(cost, 4),
                    "currency":         "USD",
                    "anomaly_injected": anomaly_flag,
                    "anomaly_reason":   anomaly_reason,
                    "resource_id":      f"/subscriptions/demo/resourceGroups/{cost_centre}/providers/Microsoft/{svc['name'].replace(' ', '')}/{region.replace(' ', '-').lower()}-001",
                })

    return pd.DataFrame(records)


def save(df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Full dataset
    full_path = OUTPUT_DIR / "azure_costs_raw.csv"
    df.to_csv(full_path, index=False)
    print(f"Saved {len(df):,} records → {full_path}")

    # Anomaly-only subset (useful for testing anomaly detector)
    anomaly_path = OUTPUT_DIR / "anomalies_ground_truth.csv"
    df[df["anomaly_injected"]].to_csv(anomaly_path, index=False)
    print(f"Saved {df['anomaly_injected'].sum()} anomaly records → {anomaly_path}")

    # Summary stats
    print("\nCost summary (USD):")
    print(f"  Total:    ${df['cost_usd'].sum():,.2f}")
    print(f"  Daily avg: ${df.groupby('date')['cost_usd'].sum().mean():,.2f}")
    print(f"  Services: {df['service_name'].nunique()}")
    print(f"  Anomalies injected: {len(ANOMALIES)}")


if __name__ == "__main__":
    print("Generating mock Azure cost data...")
    df = generate_cost_records()
    save(df)
    print("\nDone. Run the lakehouse pipeline next.")