-- Schema setup for Polymarket Trader Explorer
-- This file defines the raw and typed tables used by the ETL pipeline.

-- Drop existing tables if they exist. Order matters because of foreign keys.
DROP TABLE IF EXISTS trader_topic_share CASCADE;
DROP TABLE IF EXISTS trader_agg CASCADE;
DROP TABLE IF EXISTS staging_trader_agg CASCADE;

-- Staging table stores all fields as text. Use this table to load the
-- CSVs with `COPY` or `\copy` before casting into the typed table.
CREATE TABLE staging_trader_agg (
    trader text,
    trader_pnl text,
    trader_volume text,
    transaction_count text,
    transactions_per_day text,
    volume_per_day text,
    markets_per_day text,
    price_levels_consumed text,
    price_levels_per_transaction text,
    price_levels_consumed_vw text,
    price_levels_vw_per_transaction text,
    price_levels_per_volume text,
    mean_delta text,
    std_delta text,
    mean_time text,
    std_time text,
    mean_time_vw text,
    std_time_vw text,
    trader_ppv text,
    mean_tx_value text,
    std_tx_value text,
    trader_label text,
    largest_transformers_topic_share text,
    largest_tags_topic_share text
    -- topic columns remain in staging; they are wide and will be unpivoted
);

-- Typed table with proper numeric types and generated ROI column. This
-- representation is used by the API.
CREATE TABLE trader_agg (
    trader text PRIMARY KEY,
    trader_pnl numeric,
    trader_volume numeric,
    transaction_count integer,
    transactions_per_day numeric,
    volume_per_day numeric,
    markets_per_day numeric,
    price_levels_consumed numeric,
    price_levels_per_transaction numeric,
    price_levels_consumed_vw numeric,
    price_levels_vw_per_transaction numeric,
    price_levels_per_volume numeric,
    mean_delta numeric,
    std_delta numeric,
    mean_time numeric,
    std_time numeric,
    mean_time_vw numeric,
    std_time_vw numeric,
    trader_ppv numeric,
    mean_tx_value numeric,
    std_tx_value numeric,
    trader_label text,
    largest_transformers_topic_share numeric,
    largest_tags_topic_share numeric,
    -- ROI is computed as PnL divided by volume; use NULLIF to avoid divide by zero
    roi numeric GENERATED ALWAYS AS (trader_pnl / NULLIF(trader_volume, 0)) STORED
);

-- Long form representation of a trader's topic mix. The ETL script will
-- unpivot the wide topic columns from the staging table and populate this
-- table. Each row corresponds to a single topic share for a trader.
CREATE TABLE trader_topic_share (
    trader text REFERENCES trader_agg (trader) ON DELETE CASCADE,
    topic text NOT NULL,
    share numeric NOT NULL,
    PRIMARY KEY (trader, topic)
);