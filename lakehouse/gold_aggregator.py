import duckdb
import os

SILVER_PATH = "data/lakehouse/silver/azure_costs/azure_costs.parquet"
GOLD_PATH = "data/lakehouse/gold"

def build_gold():
    print("=== Gold Aggregator ===")

    con = duckdb.connect()

    df = con.execute(f"""
        SELECT *
        FROM read_parquet('{SILVER_PATH}')
    """).df()

    print(f"Read {len(df):,} rows from Silver")

    os.makedirs(GOLD_PATH, exist_ok=True)

    # -----------------------------------
    # 1. Daily total cost
    # -----------------------------------
    daily_costs = con.execute("""
        SELECT
            usage_date,
            SUM(cost) AS total_cost
        FROM df
        GROUP BY usage_date
        ORDER BY usage_date
    """).df()

    con.execute(f"""
        COPY daily_costs TO '{GOLD_PATH}/daily_costs.parquet' (FORMAT PARQUET)
    """)

    print(f"Created daily_costs ({len(daily_costs)} rows)")

    # -----------------------------------
    # 2. Service-level cost
    # -----------------------------------
    service_costs = con.execute("""
        SELECT
            usage_date,
            service_name,
            SUM(cost) AS service_cost
        FROM df
        GROUP BY usage_date, service_name
    """).df()

    con.execute(f"""
        COPY service_costs TO '{GOLD_PATH}/service_costs.parquet' (FORMAT PARQUET)
    """)

    print(f"Created service_costs ({len(service_costs)} rows)")

    # -----------------------------------
    # 3. Rolling baseline (7-day avg)
    # -----------------------------------
    trends = con.execute("""
        SELECT
            usage_date,
            service_name,
            service_cost,
            AVG(service_cost) OVER (
                PARTITION BY service_name
                ORDER BY usage_date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS rolling_avg_7d
        FROM service_costs
    """).df()

    con.execute(f"""
        COPY trends TO '{GOLD_PATH}/cost_trends.parquet' (FORMAT PARQUET)
    """)

    print(f"Created cost_trends ({len(trends)} rows)")

    # -----------------------------------
    # Summary
    # -----------------------------------
    print("\nGold layer summary:")
    print(f"  Days:            {daily_costs['usage_date'].nunique()}")
    print(f"  Services:        {df['service_name'].nunique()}")
    print(f"  Total cost:      ${df['cost'].sum():,.2f}")
    print(f"  Avg daily cost:  ${daily_costs['total_cost'].mean():,.2f}")

    print(f"\nWritten to → {GOLD_PATH}/")


if __name__ == "__main__":
    build_gold()