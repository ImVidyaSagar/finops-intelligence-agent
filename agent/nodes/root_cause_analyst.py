import pandas as pd

ANOMALY_PATH = "data/lakehouse/gold/anomalies_detected.parquet"
SILVER_PATH = "data/lakehouse/silver/azure_costs/azure_costs.parquet"
OUTPUT_PATH = "data/lakehouse/gold/anomaly_root_causes.parquet"


def analyze():
    print("=== Root Cause Analysis ===")

    anomalies = pd.read_parquet(ANOMALY_PATH)
    df = pd.read_parquet(SILVER_PATH)

    results = []

    for _, row in anomalies.iterrows():
        date = pd.to_datetime(row['usage_date']).date()
        service = row['service_name']

        subset = df[
            (df['usage_date'] == date) &
            (df['service_name'] == service)
        ]

        if subset.empty:
            continue

        # Region breakdown
        region_costs = subset.groupby('region')['cost'].sum().sort_values(ascending=False)

        # Chip breakdown
        chip_costs = subset.groupby('chip_family')['cost'].sum().sort_values(ascending=False)

        top_region = region_costs.idxmax()
        top_chip = chip_costs.idxmax()

        # Build explanation
        explanation = (
            f"{service} spike on {date} driven by "
            f"{top_chip} usage in {top_region}. "
            f"Total cost: ${row['service_cost']:.0f}, "
            f"{row['deviation_ratio']:.1f}x above baseline."
        )

        results.append({
            "usage_date": date,
            "service_name": service,
            "top_region": top_region,
            "top_chip": top_chip,
            "explanation": explanation
        })

    output_df = pd.DataFrame(results)
    output_df.to_parquet(OUTPUT_PATH, index=False)

    print(f"Analyzed {len(output_df)} anomalies")

    print("\nSample insights:")
    print(output_df.head(5)['explanation'])

    print(f"\nSaved → {OUTPUT_PATH}")


if __name__ == "__main__":
    analyze()