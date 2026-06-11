import duckdb
from datetime import datetime
import os

BRONZE_PATH = "data/lakehouse/bronze/azure_costs"
SILVER_PATH = "data/lakehouse/silver/azure_costs"

def transform_to_silver():
    print("=== Silver Transformer ===")

    con = duckdb.connect()

    # Read Bronze Delta table
    df = con.execute(f"""
        SELECT *
        FROM read_parquet('{BRONZE_PATH}/*.parquet')
    """).df()
    if 'cost_usd' in df.columns:
        df['cost'] = df['cost_usd']
    else:
        raise Exception("No cost column found in dataset")
    print(f"Read {len(df):,} rows from Bronze")

    # -----------------------------
    # 1. Standardize column names
    # -----------------------------
    df.columns = [col.lower() for col in df.columns]

    # -----------------------------
    # 2. Type casting
    # -----------------------------
    df['date'] = df['date'].astype('datetime64[ns]')
    df['cost'] = df['cost'].astype(float)

    # -----------------------------
    # 3. Feature engineering
    # -----------------------------
    df['usage_date'] = df['date'].dt.date
    df['day_of_week'] = df['date'].dt.day_name()
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])

    # Cost category mapping
    def map_cost_category(service):
        service = service.lower()
        if "storage" in service:
            return "storage"
        elif "network" in service or "bandwidth" in service:
            return "network"
        else:
            return "compute"

    df['cost_category'] = df['service_name'].apply(map_cost_category)

    # -----------------------------
    # 4. Data cleaning
    # -----------------------------
    before = len(df)

    df = df.dropna(subset=['cost', 'service_name', 'region'])
    df = df[df['cost'] >= 0]

    df = df.drop_duplicates()

    after = len(df)

    print(f"Cleaned rows: {before - after}")

    # -----------------------------
    # 5. Add silver metadata
    # -----------------------------
    df['_transformed_at'] = datetime.utcnow()
    df['_pipeline_layer'] = "silver"

    # -----------------------------
    # 6. Write to Silver layer
    # -----------------------------
    os.makedirs(SILVER_PATH, exist_ok=True)

    con.execute(f"""
        COPY df TO '{SILVER_PATH}/azure_costs.parquet' (FORMAT PARQUET)
    """)

    # -----------------------------
    # 7. Summary
    # -----------------------------
    print("Silver layer summary:")
    print(f"  Rows:        {len(df):,}")
    print(f"  Date range:  {df['date'].min()} → {df['date'].max()}")
    print(f"  Services:    {df['service_name'].nunique()}")
    print(f"  Categories:  {df['cost_category'].unique().tolist()}")
    print(f"  Total cost:  ${df['cost'].sum():,.2f}")

    print(f"Written to Silver → {SILVER_PATH}/azure_costs.parquet")


if __name__ == "__main__":
    transform_to_silver()