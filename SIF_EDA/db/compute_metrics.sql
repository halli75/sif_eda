-- Computed materialized views for Polymarket Trader Explorer
-- These views preaggregate expensive metrics so that the API can serve
-- responses quickly. Refresh them with `REFRESH MATERIALIZED VIEW`.

-- Drop existing views if they exist
DROP MATERIALIZED VIEW IF EXISTS trader_stats CASCADE;
DROP MATERIALIZED VIEW IF EXISTS trader_topic_metrics CASCADE;

/*
 * trader_topic_metrics
 *
 * Computes Shannon entropy and niche score for each trader based on their
 * topic share distribution. The formula for entropy is -Σ p_i * ln(p_i).
 * The niche score normalises entropy by the number of active topics: it is
 * 1 - entropy/ln(k) where k is the number of non‑zero topics. A trader
 * specialising in a single topic will have niche_score = 1; a trader
 * spreading uniformly across k topics will have niche_score = 0.
 */
CREATE MATERIALIZED VIEW trader_topic_metrics AS
WITH non_zero AS (
    SELECT trader, topic, share
    FROM trader_topic_share
    WHERE share > 0
),
agg AS (
    SELECT
        trader,
        COUNT(*)            AS active_topics,
        SUM(share * LN(share)) AS sum_p_ln_p
    FROM non_zero
    GROUP BY trader
)
SELECT
    a.trader,
    -- Shannon entropy (≥0)
    COALESCE(-1.0 * a.sum_p_ln_p, 0) AS topic_entropy,
    -- Normalised niche score
    CASE
        WHEN a.active_topics > 1 THEN 1 - ((-1.0 * a.sum_p_ln_p) / LN(a.active_topics))
        ELSE 1
    END AS niche_score,
    a.active_topics
FROM agg a;

/*
 * trader_stats
 *
 * Computes z‑scores for price impact metrics and time variability and
 * combines them into composite scores. The z‑score of a value x is
 * (x - μ) / σ where μ is the mean and σ is the population standard
 * deviation across all traders. A positive z‑score indicates a value
 * above the average, negative indicates below average.
 */
CREATE MATERIALIZED VIEW trader_stats AS
WITH stats AS (
    SELECT
        AVG(price_levels_per_transaction)   AS mean_plpt,
        STDDEV_POP(price_levels_per_transaction) AS sd_plpt,
        AVG(price_levels_per_volume)        AS mean_plpv,
        STDDEV_POP(price_levels_per_volume) AS sd_plpv,
        AVG(price_levels_vw_per_transaction)   AS mean_plvwt,
        STDDEV_POP(price_levels_vw_per_transaction) AS sd_plvwt,
        AVG(std_time_vw)                    AS mean_std_time_vw,
        STDDEV_POP(std_time_vw)             AS sd_std_time_vw
    FROM trader_agg
),
normalised AS (
    SELECT
        t.trader,
        -- z‑scores for the three impact metrics
        CASE WHEN s.sd_plpt > 0 THEN (t.price_levels_per_transaction - s.mean_plpt) / s.sd_plpt ELSE NULL END AS z_plpt,
        CASE WHEN s.sd_plpv > 0 THEN (t.price_levels_per_volume - s.mean_plpv) / s.sd_plpv ELSE NULL END AS z_plpv,
        CASE WHEN s.sd_plvwt > 0 THEN (t.price_levels_vw_per_transaction - s.mean_plvwt) / s.sd_plvwt ELSE NULL END AS z_plvwt,
        -- z‑score for time variability
        CASE WHEN s.sd_std_time_vw > 0 THEN (t.std_time_vw - s.mean_std_time_vw) / s.sd_std_time_vw ELSE NULL END AS z_std_time_vw
    FROM trader_agg t, stats s
)
SELECT
    n.trader,
    n.z_plpt,
    n.z_plpv,
    n.z_plvwt,
    n.z_std_time_vw,
    -- Impact intensity: average of the three price level z‑scores
    (n.z_plpt + n.z_plpv + n.z_plvwt) / 3.0 AS impact_intensity,
    -- Pace variability: z‑score of std_time_vw (how erratic the pacing is)
    n.z_std_time_vw AS pace_variability
FROM normalised n;