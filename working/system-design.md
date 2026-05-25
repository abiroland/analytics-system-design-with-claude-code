# Avocado Sales Analytics System — System Design

## Problem

We have weekly avocado pricing and volume data across 54 US regions (2015-2018, 18,249 rows). The business needs to understand what drives avocado prices, how demand varies by region and type (conventional vs organic), and where to allocate supply for maximum revenue.

The data has a structural trap: the 54 "regions" mix city-level markets (Albany, Atlanta), state-level (California), and pre-computed aggregates (TotalUS, West, Southeast). Any analysis that treats these as peers will double-count volume and produce garbage correlations. The system must enforce separation at the preprocessing layer.

### Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| (unnamed) | int | Row index — redundant, drop |
| Date | string | Observation date, DD/MM/YYYY format |
| AveragePrice | float | Average selling price per avocado |
| Total Volume | float | Total units sold (range: 84 to 62.5M) |
| 4046 | float | Volume of PLU 4046 (small Hass) |
| 4225 | float | Volume of PLU 4225 (large Hass) |
| 4770 | float | Volume of PLU 4770 (extra-large Hass) |
| Total Bags | float | Total bagged avocados sold |
| Small Bags | float | Small bag volume |
| Large Bags | float | Large bag volume |
| XLarge Bags | float | Extra-large bag volume |
| type | string | "conventional" or "organic" |
| year | int | 2015, 2016, 2017, or 2018 |
| region | string | One of 54 geographic regions |

Weekly granularity. No missing values. Clean schema throughout.

---

## Analytical Framework

A senior data scientist approaches this in four layers. Each layer answers a different question, and each layer's output feeds the next.

| Layer | Question | What It Produces |
|-------|----------|-----------------|
| **Descriptive** | What happened? | Trends, distributions, seasonality, product mix shares |
| **Diagnostic** | Why did it happen? | Correlations, regional drivers, organic premium decomposition |
| **Predictive** | What will happen? | Price/volume forecasts, growth market identification |
| **Prescriptive** | What should we do? | Revenue-optimal pricing, regional allocation, mix optimization |

Skipping layers produces unfounded conclusions. Prescriptive without diagnostic = recommendations without evidence. Predictive without descriptive = forecasting patterns you haven't verified exist.

---

## System Spec

### Agent Contracts

```
┌─────────────────────────────────────────────────────────────────────┐
│ AGENT CONTRACT: descriptive_analysis                                │
├─────────────────────────────────────────────────────────────────────┤
│ Name:        Descriptive Analyst                                    │
│ Description: Fires when new or updated data lands in               │
│              data/processed/avocado_features.csv and no             │
│              descriptive report exists for today's date. Computes   │
│              trend lines, seasonal decomposition, distribution      │
│              stats, and product mix shares for city-level regions.  │
│ Inputs:      data/processed/avocado_features.csv                   │
│ Outputs:     outputs/descriptive_report_YYYY-MM-DD.md              │
│              outputs/charts/desc_*.png                              │
│ Depends On:  src/data_prep.py (must have run first)                │
│ Skills Used: seasonality_decomposition, regional_comparison,        │
│              chart_generator                                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ AGENT CONTRACT: diagnostic_analysis                                 │
├─────────────────────────────────────────────────────────────────────┤
│ Name:        Diagnostic Analyst                                     │
│ Description: Fires after descriptive_analysis completes and its     │
│              report exists at outputs/descriptive_report_*.md.      │
│              Reads the patterns surfaced there and tests causal     │
│              hypotheses: price-volume correlations, regional        │
│              drivers of national trends, organic premium            │
│              decomposition by region and season.                    │
│ Inputs:      data/processed/avocado_features.csv                   │
│              outputs/descriptive_report_YYYY-MM-DD.md               │
│ Outputs:     outputs/diagnostic_report_YYYY-MM-DD.md               │
│              outputs/charts/diag_*.png                              │
│ Depends On:  descriptive_analysis                                   │
│ Skills Used: price_elasticity, regional_comparison,                 │
│              chart_generator                                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ AGENT CONTRACT: predictive_analysis                                 │
├─────────────────────────────────────────────────────────────────────┤
│ Name:        Predictive Analyst                                     │
│ Description: Fires after diagnostic_analysis completes and its      │
│              report exists at outputs/diagnostic_report_*.md.       │
│              Uses the validated features and drivers from that      │
│              report to build ARIMA/Prophet forecasts of price and   │
│              volume by region and type, with accuracy metrics on    │
│              a held-out test set.                                   │
│ Inputs:      data/processed/avocado_features.csv                   │
│              outputs/diagnostic_report_YYYY-MM-DD.md                │
│ Outputs:     outputs/predictive_report_YYYY-MM-DD.md               │
│              outputs/models/forecast_*.pkl                          │
│              outputs/charts/pred_*.png                              │
│ Depends On:  diagnostic_analysis                                    │
│ Skills Used: seasonality_decomposition, forecast_engine,            │
│              chart_generator                                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ AGENT CONTRACT: prescriptive_analysis                               │
├─────────────────────────────────────────────────────────────────────┤
│ Name:        Prescriptive Analyst                                   │
│ Description: Fires after both diagnostic and predictive reports     │
│              exist. Combines elasticity estimates from diagnostic   │
│              with demand forecasts from predictive to compute       │
│              revenue-maximizing price points by region/type,        │
│              regional volume allocation, and optimal                │
│              organic/conventional mix.                              │
│ Inputs:      data/processed/avocado_features.csv                   │
│              outputs/diagnostic_report_YYYY-MM-DD.md                │
│              outputs/predictive_report_YYYY-MM-DD.md                │
│ Outputs:     outputs/prescriptive_report_YYYY-MM-DD.md             │
│              outputs/charts/presc_*.png                             │
│ Depends On:  predictive_analysis                                    │
│ Skills Used: price_elasticity, chart_generator                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ AGENT CONTRACT: executive_summary                                   │
├─────────────────────────────────────────────────────────────────────┤
│ Name:        Executive Writer                                       │
│ Description: Fires when all four reports (descriptive, diagnostic,  │
│              predictive, prescriptive) exist for today's date.      │
│              Reads all four, extracts the 3-5 highest-impact        │
│              findings, translates metrics into business language,   │
│              and writes a one-page leadership readout with          │
│              recommendations and risk callouts.                     │
│ Inputs:      outputs/descriptive_report_YYYY-MM-DD.md              │
│              outputs/diagnostic_report_YYYY-MM-DD.md                │
│              outputs/predictive_report_YYYY-MM-DD.md                │
│              outputs/prescriptive_report_YYYY-MM-DD.md              │
│ Outputs:     outputs/executive_summary_YYYY-MM-DD.md               │
│ Depends On:  prescriptive_analysis                                  │
│ Skills Used: (none — pure synthesis and writing)                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Skill Specs

**`seasonality_decomposition`**
- **Description:** Performs STL decomposition on a specified numeric column, grouped by region and type. Returns trend, seasonal, and residual components.
- **Trigger:** Fires when an agent needs to isolate seasonal patterns from trend — specifically when analyzing time series behavior or preparing features for forecasting.
- **Inputs:** DataFrame, column name, grouping keys (region, type), period (default 52 for weekly).
- **Outputs:** DataFrame with `_trend`, `_seasonal`, `_residual` suffix columns appended. Summary stats of seasonal amplitude by group.

**`price_elasticity`**
- **Description:** Computes point price elasticity via log-log OLS regression of volume on price, segmented by region and type. Reports coefficient, R², p-value, and confidence interval.
- **Trigger:** Fires when an agent needs to quantify how volume responds to price changes — in diagnostic context (explaining volume swings) or prescriptive context (optimizing price).
- **Inputs:** DataFrame with `AveragePrice` and `Total Volume` columns, grouping keys.
- **Outputs:** Elasticity table: one row per group with elasticity coefficient, standard error, R², p-value, 95% CI. Interpretation flag: elastic (|e|>1), inelastic (|e|<1), unit elastic.

**`regional_comparison`**
- **Description:** Ranks regions on a specified metric (price, volume, growth rate, elasticity) and optionally clusters them using k-means on standardized features.
- **Trigger:** Fires when an agent needs to compare regions — identifying top/bottom performers, grouping similar markets, or finding outliers.
- **Inputs:** DataFrame, metric column(s), number of clusters (default 4), region_level filter (default "city" — excludes aggregates).
- **Outputs:** Ranked table with percentile scores. Cluster assignments with cluster centroids. Outlier flags (>2σ from cluster centroid).

**`forecast_engine`**
- **Description:** Fits ARIMA (auto-order via AIC) or Prophet model on a time series, evaluates on held-out period, returns forecasts with prediction intervals.
- **Trigger:** Fires when an agent needs forward-looking projections — price forecasts, volume trajectories, or growth market identification.
- **Inputs:** Time series DataFrame, target column, forecast horizon (default 26 weeks), train/test split ratio (default 0.8), model type ("arima" or "prophet").
- **Outputs:** Forecast DataFrame with point estimate + 80%/95% prediction intervals. Accuracy metrics on test set: RMSE, MAE, MAPE. Model artifact saved to `outputs/models/`.

**`chart_generator`**
- **Description:** Produces publication-quality matplotlib/seaborn charts with consistent styling — labeled axes, legend, no chartjunk, 300 DPI PNG output.
- **Trigger:** Fires whenever an agent needs to produce a visualization. All chart creation routes through this skill for visual consistency.
- **Inputs:** Chart type (line, bar, heatmap, scatter, box), data, x/y columns, grouping, title, filename prefix.
- **Outputs:** PNG file saved to `outputs/charts/{prefix}_{timestamp}.png`. Returns file path for embedding in reports.

### Knowledge — What the System Remembers Across Sessions

1. **Region classification map** — which of the 54 regions are city-level, state-level, or aggregate. Determined during data exploration, must not be re-derived each time.
2. **Baseline metrics** — the first descriptive run's key numbers (national avg price by type, total volume, top 5 regions by volume). Future runs compare against these to detect drift or data issues.
3. **Elasticity reference values** — elasticity coefficients by region/type from the most recent diagnostic run. Prescriptive agent uses these without re-computing unless data changes.

### Invariants

1. **Never mix aggregation levels in statistical analysis.** City-level regions (Albany, Atlanta) and aggregate regions (TotalUS, West, Southeast) must never appear in the same groupby, correlation, or regression. Aggregates double-count city data. The `region_level` column exists to enforce this — filter to `city` by default.

2. **Never overwrite raw data or prior outputs.** `data/raw/` is immutable. Reports in `outputs/` are date-stamped — a new run creates a new file, never overwrites yesterday's report. If `outputs/descriptive_report_2026-05-25.md` exists and the agent runs again on 2026-05-25, it appends a sequence number (`_v2`).

3. **Never report a result without citing its source table.** Every number, trend, or claim in a report must state which data file and which columns produced it. "Organic prices rose 12%" is incomplete — "Organic prices rose 12% (avocado_features.csv, AveragePrice where type='organic', 2015 vs 2018)" is valid. If a result combines multiple tables, cite all of them.

4. **Never present a downstream result without its upstream dependency having run.** Prescriptive agent cannot run without predictive and diagnostic outputs. Executive summary cannot run without all four reports. The chain is strict: if a dependency is missing, the agent fails loudly with the missing file path — it does not hallucinate or substitute.

---

## Build Plan — File-by-File, In Order

```
STEP  FILE                                              DEPENDS ON        WHAT IT IS
────  ────                                              ──────────        ──────────
 1    src/data_prep.py                                  data/raw/avocado.csv
                                                                          Python script: drops index col, parses
                                                                          dates, classifies regions into city/state/
                                                                          aggregate, engineers features. Writes
                                                                          data/processed/avocado_clean.csv and
                                                                          data/processed/avocado_features.csv.
                                                                          RUN IT after creating.

 2    .claude/skills/chart-generator/skill.md            nothing
                                                                          Skill prompt: standardized matplotlib/seaborn
                                                                          chart production. Every agent uses this —
                                                                          build it first so all downstream agents
                                                                          have it.

 3    .claude/skills/seasonality-decomposition/skill.md  nothing
                                                                          Skill prompt: STL decomposition on a time
                                                                          series column grouped by region/type.
                                                                          Needed by descriptive + predictive agents.

 4    .claude/skills/regional-comparison/skill.md        nothing
                                                                          Skill prompt: ranks and clusters regions on
                                                                          any metric, filters out aggregates by default.
                                                                          Needed by descriptive + diagnostic agents.

 5    agents/descriptive_analysis.md                     steps 1-4
                                                                          Agent prompt: reads avocado_features.csv,
                                                                          produces trend/seasonality/distribution/mix
                                                                          report. First agent in chain — everything
                                                                          downstream waits on its output.

      >>> CHECKPOINT: run descriptive agent, verify outputs/descriptive_report_*.md exists

 6    .claude/skills/price-elasticity/skill.md           nothing
                                                                          Skill prompt: log-log OLS of volume on price
                                                                          by region/type. Reports elasticity, R², CI.
                                                                          Needed by diagnostic + prescriptive agents.

 7    agents/diagnostic_analysis.md                      steps 5, 6
                                                                          Agent prompt: reads descriptive report +
                                                                          processed data. Tests causal hypotheses,
                                                                          decomposes organic premium, identifies
                                                                          regional drivers.

      >>> CHECKPOINT: run diagnostic agent, verify outputs/diagnostic_report_*.md exists

 8    .claude/skills/forecast-engine/skill.md            nothing
                                                                          Skill prompt: ARIMA/Prophet wrapper with
                                                                          train-test split, accuracy metrics, prediction
                                                                          intervals. Needed by predictive agent.

 9    agents/predictive_analysis.md                      steps 7, 8
                                                                          Agent prompt: reads diagnostic report +
                                                                          processed data. Builds price/volume forecasts
                                                                          by region/type. Saves model artifacts.

      >>> CHECKPOINT: run predictive agent, verify outputs/predictive_report_*.md exists

10    agents/prescriptive_analysis.md                    steps 7, 9
                                                                          Agent prompt: reads diagnostic + predictive
                                                                          reports. Computes revenue-optimal prices,
                                                                          regional allocation, organic/conventional mix.

      >>> CHECKPOINT: run prescriptive agent, verify outputs/prescriptive_report_*.md exists

11    agents/executive_summary.md                        steps 5, 7, 9, 10
                                                                          Agent prompt: reads all four reports. Extracts
                                                                          top 3-5 findings, translates to business
                                                                          language, writes one-page leadership readout.

      >>> FINAL: run executive summary agent, verify it references all four upstream reports
```

### Dependency Graph

```
data/raw/avocado.csv
       │
       ▼
  [1] src/data_prep.py ──► data/processed/*
       │
       ├──── [2] chart_generator ◄──────────────────────────── (used by all agents)
       ├──── [3] seasonality_decomposition
       ├──── [4] regional_comparison
       │
       ▼
  [5] descriptive_analysis agent
       │
       ├──── [6] price_elasticity
       │
       ▼
  [7] diagnostic_analysis agent
       │
       ├──── [8] forecast_engine
       │
       ▼
  [9] predictive_analysis agent
       │
       ▼
 [10] prescriptive_analysis agent
       │
       ▼
 [11] executive_summary agent
```

### What Can Be Built in Parallel

- Steps 2, 3, 4 (skills with no dependencies) — can all be built at same time
- Step 6 (price_elasticity) can be built anytime before step 7
- Step 8 (forecast_engine) can be built anytime before step 9
- Agents are strictly sequential: 5 → 7 → 9 → 10 → 11

### Verification

At each `>>> CHECKPOINT`:
1. Output report file exists with today's date
2. Report cites source table + columns for every claim (invariant #3)
3. No aggregate regions (TotalUS, West) in city-level analysis (invariant #1)
4. No prior output files overwritten (invariant #2)
5. Final: executive summary references findings from all four layer reports
