"""
bronze_writer.py
Reads raw CSV from data/mock/ and writes to Bronze Delta Lake table.
Bronze = raw, unmodified, append-only. Just add metadata columns.
"""

import duckdb
import pandas as pd
from deltalake import write_deltalake
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT         = Path(__file__).parent.parent
RAW_CSV      = ROOT / "data" / "mock" / "azure_costs_raw.csv"
BRONZE_PATH  = str(ROOT / "data" / "lakehouse" / "bronze" / "azure_costs")

# ── Bronze writer ─────────────────────────────────────────────────────────────

def read_raw(path: Path) -> pd.DataFrame:
    con = duckdb.connect()
    df = con.execute(f"SELECT * FROM read_csv_auto('{path}')").df()
    print(f"Read {len(df):,} rows from {path.name}")
    return df


def add_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bronze rule: never change source data.
    Only add ingestion metadata columns.
    """
    now = datetime.now(timezone.utc).isoformat()
    df = df.copy()
    df["_ingested_at"]    = now
    df["_source_file"]    = RAW_CSV.name
    df["_pipeline_layer"] = "bronze"
    return df


def write_bronze(df: pd.DataFrame) -> None:
    Path(BRONZE_PATH).mkdir(parents=True, exist_ok=True)

    write_deltalake(
        BRONZE_PATH,
        df,
        mode="overwrite",       # idempotent for local dev
        schema_mode="overwrite",
    )
    print(f"Written to Bronze Delta table → {BRONZE_PATH}")


def validate(df: pd.DataFrame) -> None:
    """Basic schema checks before writing."""
    required = ["date", "service_name", "cost_usd", "chip_family", "region", "environment"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    nulls = df[required].isnull().sum()
    null_cols = nulls[nulls > 0]
    if not null_cols.empty:
        print(f"Warning — null values found:\n{null_cols}")

    print("Schema validation passed.")


def summarise(df: pd.DataFrame) -> None:
    print("\nBronze layer summary:")
    print(f"  Rows:        {len(df):,}")
    print(f"  Date range:  {df['date'].min()} → {df['date'].max()}")
    print(f"  Services:    {df['service_name'].nunique()}")
    print(f"  Regions:     {df['region'].nunique()}")
    print(f"  Total cost:  ${df['cost_usd'].sum():,.2f}")
    print(f"  Chip families: {sorted(df['chip_family'].unique().tolist())}")


if __name__ == "__main__":
    print("=== Bronze Writer ===")
    df_raw    = read_raw(RAW_CSV)
    validate(df_raw)
    df_bronze = add_metadata(df_raw)
    write_bronze(df_bronze)
    summarise(df_bronze)
    print("\nDone. Run silver_transformer.py next.")