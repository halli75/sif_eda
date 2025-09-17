"""
ETL script for the Polymarket Trader dataset.

This script loads the three CSV parts produced from the original
`traders.csv`, concatenates them, converts the text fields into
appropriate types, unpivots the topic columns into a long form table,
and inserts all data into a PostgreSQL database. It also refreshes
materialized views defined in `db/compute_metrics.sql`.

Usage:
    python etl.py --db-url postgresql://user:pass@localhost/dbname \
                  --csv-dir /path/to/csv_parts

You must have the `psycopg2-binary` and `pandas` packages installed. The
script uses SQLAlchemy for database interactions and pandas for CSV
parsing. For large datasets consider specifying `chunksize` when
calling `read_csv`.
"""
import argparse
import os
import pandas as pd
from sqlalchemy import create_engine, text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load trader CSV parts into Postgres")
    parser.add_argument("--db-url", required=True, help="SQLAlchemy database URL, e.g. postgresql://user:pass@host/db")
    parser.add_argument("--csv-dir", required=True, help="Directory containing the three CSV parts")
    return parser.parse_args()


def load_csv_parts(csv_dir: str) -> pd.DataFrame:
    """Read and concatenate all CSV parts into a single DataFrame."""
    parts = []
    for filename in sorted(os.listdir(csv_dir)):
        if filename.lower().endswith(".csv"):
            path = os.path.join(csv_dir, filename)
            print(f"Reading {path}")
            df_part = pd.read_csv(path, low_memory=False)
            parts.append(df_part)
    if not parts:
        raise RuntimeError(f"No CSV files found in {csv_dir}")
    df = pd.concat(parts, ignore_index=True)
    return df


def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast columns from string to appropriate numeric types. Missing values
    remain as NaN (which maps to NULL in SQL). Additional columns not
    listed here remain as objects (strings) and will be ignored when
    inserting into the typed table.
    """
    numeric_cols = [
        "trader_pnl",
        "trader_volume",
        "transaction_count",
        "transactions_per_day",
        "volume_per_day",
        "markets_per_day",
        "price_levels_consumed",
        "price_levels_per_transaction",
        "price_levels_consumed_vw",
        "price_levels_vw_per_transaction",
        "price_levels_per_volume",
        "mean_delta",
        "std_delta",
        "mean_time",
        "std_time",
        "mean_time_vw",
        "std_time_vw",
        "trader_ppv",
        "mean_tx_value",
        "std_tx_value",
        "largest_transformers_topic_share",
        "largest_tags_topic_share",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "transaction_count" in df.columns:
        df["transaction_count"] = df["transaction_count"].astype("Int64")
    return df


def unpivot_topics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert wide topic columns (those starting with 'topic_') into a long
    form DataFrame with columns [trader, topic, share]. Only topics with
    non‑zero share are retained. Topics are renamed by stripping the
    'topic_' prefix and normalising spaces and punctuation.
    """
    topic_cols = [c for c in df.columns if c.lower().startswith("topic_")]
    if not topic_cols:
        return pd.DataFrame(columns=["trader", "topic", "share"])
    long_df = df[["trader"] + topic_cols].melt(
        id_vars=["trader"],
        var_name="topic",
        value_name="share",
    )
    # Drop rows where share is null or zero
    long_df = long_df.dropna(subset=["share"])
    long_df = long_df[long_df["share"] != 0]
    # Normalise topic names: remove 'topic_' prefix and collapse whitespace
    long_df["topic"] = long_df["topic"].str.replace("topic_", "", regex=False)
    long_df["topic"] = long_df["topic"].str.strip()
    return long_df[["trader", "topic", "share"]]


def insert_data(engine, df: pd.DataFrame, long_topics: pd.DataFrame) -> None:
    """
    Insert data into the typed tables using SQLAlchemy. Data is inserted
    into `trader_agg` and `trader_topic_share`. Existing data is truncated
    before inserting.
    """
    with engine.begin() as conn:
        # Truncate tables
        conn.execute(text("TRUNCATE trader_topic_share RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE trader_agg RESTART IDENTITY CASCADE"))
        # Insert into trader_agg – restrict to columns defined in the table
        cols = [
            "trader",
            "trader_pnl",
            "trader_volume",
            "transaction_count",
            "transactions_per_day",
            "volume_per_day",
            "markets_per_day",
            "price_levels_consumed",
            "price_levels_per_transaction",
            "price_levels_consumed_vw",
            "price_levels_vw_per_transaction",
            "price_levels_per_volume",
            "mean_delta",
            "std_delta",
            "mean_time",
            "std_time",
            "mean_time_vw",
            "std_time_vw",
            "trader_ppv",
            "mean_tx_value",
            "std_tx_value",
            "trader_label",
            "largest_transformers_topic_share",
            "largest_tags_topic_share",
        ]
        df[cols].to_sql(
            name="trader_agg",
            con=conn,
            if_exists="append",
            index=False,
            method="multi",
        )
        # Insert into trader_topic_share
        if not long_topics.empty:
            long_topics.to_sql(
                name="trader_topic_share",
                con=conn,
                if_exists="append",
                index=False,
                method="multi",
            )


def refresh_materialized_views(engine) -> None:
    """Refresh the materialized views to compute metrics."""
    with engine.begin() as conn:
        conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY trader_topic_metrics"))
        conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY trader_stats"))


def main() -> None:
    args = parse_args()
    engine = create_engine(args.db_url)
    print("Loading CSV parts...")
    df = load_csv_parts(args.csv_dir)
    print(f"Loaded {len(df)} rows")
    print("Casting numeric columns...")
    df = cast_types(df)
    print("Unpivoting topic columns...")
    long_topics = unpivot_topics(df)
    print(f"Generated {len(long_topics)} topic rows")
    print("Inserting into database...")
    insert_data(engine, df, long_topics)
    print("Refreshing materialized views...")
    refresh_materialized_views(engine)
    print("Done!")


if __name__ == "__main__":
    main()