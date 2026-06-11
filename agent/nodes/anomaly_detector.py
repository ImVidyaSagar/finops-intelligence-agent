import duckdb
import pandas as pd

TRENDS_PATH = "data/lakehouse/gold/cost_trends.parquet"
OUTPUT_PATH = "data/lakehouse/gold/anomalies_detected.parquet"

def detect_anomalies():
    print("=== Anomaly Detector ===")

    con = duckdb.connect()

    df = con.execute(f"""
        SELECT *
        FROM read_parquet('{TRENDS_PATH}')
    """).df()

    print(f"Loaded {len(df):,} rows")

    # -----------------------------------
    # Drop rows where rolling avg is null
    # (first 7 days)
    # -----------------------------------
    df = df.dropna(subset=['rolling_avg_7d'])

    # -----------------------------------
    # Anomaly condition
    # -----------------------------------
    df['deviation_ratio'] = df['service_cost'] / df['rolling_avg_7d']

    # Calculate std deviation per service
    df['std_dev'] = df.groupby('service_name')['service_cost'].transform('std')

    # Avoid division issues
    df['std_dev'] = df['std_dev'].fillna(1)

    # Z-score
    df['z_score'] = (df['service_cost'] - df['rolling_avg_7d']) / df['std_dev']

    df['cost_diff'] = df['service_cost'] - df['rolling_avg_7d']

    df['is_anomaly'] = (
        (df['z_score'] > 2.5) &
        (df['cost_diff'] > 300)
    )
    df = df[df['service_cost'] > 200]
    anomalies = df[df['is_anomaly']].copy()

    # -----------------------------------
    # Add severity
    # -----------------------------------
    def severity(ratio):
        if ratio > 2.5:
            return "critical"
        elif ratio > 1.8:
            return "high"
        else:
            return "medium"

    anomalies['severity'] = anomalies['deviation_ratio'].apply(severity)

    # -----------------------------------
    # Save results
    # -----------------------------------
    anomalies.to_parquet(OUTPUT_PATH, index=False)

    # -----------------------------------
    # Summary
    # -----------------------------------
    print(f"Detected anomalies: {len(anomalies)}")

    print("\nSeverity breakdown:")
    print(anomalies['severity'].value_counts())

    print("\nTop anomalies:")
    print(
        anomalies.sort_values("deviation_ratio", ascending=False)
        .head(5)[['usage_date', 'service_name', 'service_cost', 'rolling_avg_7d', 'deviation_ratio']]
    )

    print(f"\nSaved → {OUTPUT_PATH}")


if __name__ == "__main__":
    detect_anomalies()