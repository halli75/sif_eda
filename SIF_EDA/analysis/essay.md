# Polymarket Trader Behaviour – Exploratory Analysis

## Introduction

The **Polymarket trader** dataset contains aggregated statistics about individual traders on the Polymarket prediction market.  Rather than raw transaction‐level data, each row summarises one trader’s activity across all topics, making this a *cross‑sectional* snapshot.  For each trader we know their total profit and loss (`trader_pnl`), trading volume (`trader_volume`), number of transactions, average volume per day, microstructure footprints (e.g. price levels consumed), timing statistics for trades, and a set of topic shares indicating how the trader splits their activity across high‑level categories such as politics, economy, sport, science or arts.  The dataset also includes a categorical **trader label**, presumably derived from previous behaviour (“sharp”, “good”, “bad” etc.).

Because the original CSV exceeded upload limits, the data was split into three parts and committed via Git LFS.  The software portion of this project therefore includes scripts to ingest those parts into a PostgreSQL database, cast string fields to numeric types, handle missing values and duplicate rows, and compute additional metrics on top of the raw fields.  This essay summarises the methodology behind those computations and the kinds of insights that a thorough exploratory data analysis (EDA) could yield.

## Data quality and ingestion

Data quality is paramount.  When importing the CSVs into PostgreSQL the ETL script (`backend/etl.py`) reads each file in streaming mode to avoid memory exhaustion, then converts blank strings to `NULL` and casts numeric columns to appropriate types.  It populates a *staging* table that mirrors the raw schema and then inserts into a typed table `trader_agg`, trimming whitespace and coalescing duplicate trader IDs.  Additional tables and views compute derived fields.

Common data issues were anticipated and handled in the pipeline:

* **Missing values and zero denominators**: Many rows have empty cells for volume or profit.  ROI is defined as `trader_pnl / trader_volume`, but dividing by zero yields undefined results.  The ETL script uses `NULLIF(trader_volume,0)` in SQL to avoid division by zero and stores ROI as `NULL` when volume is zero.  Downstream charts must filter out missing ROI values.
* **Outliers**: Predictive markets attract a few whales with extremely large volume and profit.  Distributions of `trader_pnl` and `trader_volume` were therefore expected to be heavy‑tailed.  To visualise them appropriately, the frontend uses logarithmic scales for histograms and quantile trims when computing summary statistics.
* **Topic shares**: The dataset provides columns such as `topic_politics`, `topic_sport`, etc. with values between 0 and 1 that sum to 1 for each trader.  The ETL unpivots these wide columns into a long form table `trader_topic_share(trader, topic, share)` and computes entropy‐based measures on top.

## Feature engineering

Three key derived metrics are computed in SQL views to capture how diversified, impactful and regular each trader is.

1. **Return on investment (ROI)** — defined as `trader_pnl / trader_volume`.  This metric normalises profit by the capital deployed, allowing comparison between high‑volume whales and low‑volume tourists.  ROI values can be positive or negative; a robust EDA should examine both the distribution and the volatility of ROI across traders.

2. **Topic entropy and niche score** — A trader’s topic distribution forms a probability vector whose uncertainty can be measured by Shannon’s entropy.  If a trader splits their activity across topics with probabilities \(p_i\), the entropy is

\[
H = -\sum_i p_i \log p_i,
\]

where \(-p_i \log p_i\) is the information content of choosing topic \(i\).  The base of the logarithm determines units; for example log 2 yields bits (known as *shannons*)【862634324902307†L124-L152】.  Entropy is zero when all the mass is concentrated in a single topic and increases as the distribution spreads out.  It reaches its maximum value of \(\log k\) when a trader divides their activity evenly across \(k\) active topics【862634324902307†L124-L152】.  To compare traders with different numbers of active topics, we define a **niche score**

\[
\text{niche\_score} = 1 - \frac{H}{\log k},
\]

where \(k\) is the number of non‑zero topic shares.  This score lies in \([0,1]\).  A value near 1 indicates a highly specialised trader (low entropy), whereas values near 0 correspond to diversified traders.

3. **Impact intensity and pace variability** — The dataset includes microstructure fields such as `price_levels_per_transaction`, `price_levels_per_volume` and `price_levels_vw_per_transaction` that measure how many price ticks a trader’s orders move per unit of size or per trade.  Because these metrics are on different scales, they are normalised by computing their **z‑scores**: subtracting the population mean from an individual value and dividing the difference by the population standard deviation【117481834741321†L167-L176】.  This process, known as *standardising*, produces a standard score indicating how many standard deviations a value lies above or below the mean【117481834741321†L167-L176】.  The impact intensity is defined as the average of the z‑scores for the three price impact metrics.  Similarly, `std_time_vw` quantifies how irregular a trader’s timing is; its z‑score becomes the **pace variability** metric.  High positive values indicate above‑average price impact or timing variability, while negative values signify below‑average impact or steadier pacing.

These features summarise complex behaviours in a few interpretable numbers.  They also serve as inputs to clustering algorithms for identifying archetypes.

## Potential insights from exploratory analysis

Although the full dataset was not accessible within this environment (Git LFS pointers prevent downloading the actual rows), the software is designed to support deep EDA when the data is available.  Based on typical patterns in betting markets, we outline a few analyses the app can perform and the questions it could answer.

### Profit and volume concentration

One of the first questions is: **who really wins?**  A Lorenz curve or histogram of total profit and volume would reveal heavy concentration: a small fraction of traders (perhaps the top 5 %) likely capture the majority of total profit and deploy most of the capital.  This concentration can be quantified by computing the share of aggregate |PnL| and volume accounted for by the top 1 %, 5 % and 10 % of traders ranked by those metrics.  A high Herfindahl–Hirschman index (HHI) for profit or volume would indicate a “winner‑take‑all” market structure.  Such analysis also highlights the long tail of small, unprofitable participants who provide liquidity but rarely win big.

### Label effects and fairness

The dataset includes a `trader_label` field.  The intention of the “Label Audit” view is to examine whether these labels correlate with performance after controlling for scale.  For example, does the “sharp” label correspond to higher ROI or PPV (profit per volume) even after accounting for differences in volume, number of transactions and number of markets traded?  A simple OLS regression of ROI on dummy variables for each label, with controls for log(volume) and transaction count, could reveal whether label effects remain significant.  Bootstrap confidence intervals would provide uncertainty estimates.  If the effect vanishes after controls, it suggests that the label is capturing activity scale rather than genuine edge.

### Footprint vs. edge

The “Footprint” view plots impact intensity against ROI or PPV.  One hypothesis is that traders who consume more price levels per unit volume (i.e. have a large footprint) tend to pay more market impact costs and thus exhibit lower ROI.  A scatter plot with a trend line and partial residuals can visualise this relationship.  Quantile regression could identify whether the negative correlation is stronger at extreme quantiles of ROI, highlighting how high‑impact traders perform in the tails.  Another dimension is pace variability: do irregular traders (high timing variability) achieve higher or lower profitability?  These questions become tractable once the metrics are computed.

### Topic specialisation

Using the topic unpivot table, the “Topic Studio” allows users to explore a single trader’s focus areas and compare them with cohort averages.  Topic entropy and niche score summarise diversification, but analysts can also look at specific topics: are politics specialists more profitable than sports specialists?  Does mixing unrelated topics correlate with inconsistent returns?  Regression of ROI on niche score and topic dummies would help answer these questions.  Histograms of niche score might show bimodal patterns—some traders dabble widely, others specialise narrowly.

### Archetypes and clustering

Combining all features—scale (volume, transaction count), footprint (impact intensity), pacing (pace variability), topic diversity (entropy), and performance (ROI)—we can perform unsupervised clustering to identify **trader archetypes**.  Possible clusters include:

* **Market makers** — high volume, low ROI, low impact intensity; provide liquidity and profit from bid‑ask spread.
* **Momentum tourists** — moderate volume, high impact intensity, negative ROI; chase trends and pay high market impact.
* **Event snipers** — low volume, high ROI, highly specialised (niche score near 1); trade only on specific news.
* **Diversified whales** — very high volume, moderate ROI, low entropy; allocate capital across many topics to capture risk premia.

Evaluating cluster stability under bootstrap resampling ensures that archetypes are not artefacts of random noise.  Once clusters are defined, we can examine how labels align with them; if the “sharp” label mostly appears in the Event Sniper cluster, the label may be capturing specialist behaviour.

## Limitations and future work

This project operates under several constraints.  The analysis is cross‑sectional: without timestamps for individual trades, we cannot compute rolling Sharpe ratios, drawdowns or out‑of‑sample performance.  The dataset was provided in three pieces via Git LFS; the actual rows were not accessible in this environment, so numeric summaries presented here remain conceptual.  Label definitions are unknown and may be derived from future information, raising the risk of target leakage.  Additionally, topic categories may be broad, causing entropy to underestimate the true diversification across fine‑grained markets.

In a production setting, further steps would include:

* **Data validation**: cross‑checking volumes and profits with raw trade logs; verifying that topic shares sum to one and that labels are assigned at the time of observation.
* **Time series analysis**: if timestamps become available, compute cumulative PnL curves, max drawdown, Sharpe ratios, turnover rates, and rolling performance to detect behaviour changes.
* **Causal inference**: exploring whether topic specialisation or microstructure behaviour causes differences in profitability, using methods like propensity score matching or instrumental variables.

## Conclusion

Building on this dataset, the `SIF_EDA` project creates a reproducible pipeline for loading, validating and enriching Polymarket trading data.  Derived features such as ROI, topic entropy, niche score, impact intensity and pace variability compress complex behaviour into interpretable metrics.  With these tools, an exploratory analysis can answer questions about who wins, whether labels predict edge, how market impact affects profitability, and what trader archetypes exist.  While the absence of trade‑level time series limits certain analyses, the cross‑sectional snapshot still reveals structural patterns in prediction markets.  As more detailed data becomes available, the architecture outlined here will support deeper investigations and more accurate insights.