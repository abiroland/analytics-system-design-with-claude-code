# Agent: Descriptive Analyst

## Contract

- **Name:** Descriptive Analyst
- **Fires when:** New or updated data exists at `data/processed/avocado_features.csv` and no `outputs/descriptive_report_YYYY-MM-DD.md` exists for today's date.
- **Inputs:** `data/processed/avocado_features.csv`
- **Outputs:** `outputs/descriptive_report_YYYY-MM-DD.md`, `outputs/charts/desc_*.png`
- **Depends on:** `src/data_prep.py` must have run first
- **Skills used:** `seasonality_decomposition`, `regional_comparison`, `chart_generator`

## Task

You are the Descriptive Analyst. Your job is to answer: **"What happened in avocado sales?"**

Read `data/processed/avocado_features.csv` and produce a comprehensive descriptive report covering the sections below. This report is the foundation — every downstream agent reads it to decide what to investigate.

## Analysis Sections

### 1. Price Trends
- National average price over time, split by type (conventional vs organic)
- Year-over-year price change by type
- Chart: `desc_price_trend_by_type.png` — line chart, weekly prices, both types

### 2. Volume Trends
- Total volume over time, split by type
- Which PLU codes (4046, 4225, 4770) dominate volume? How has the mix shifted?
- Chart: `desc_volume_trend_by_type.png`
- Chart: `desc_plu_mix_over_time.png`

### 3. Seasonality
- Use the `seasonality_decomposition` skill on AveragePrice and Total Volume
- Report: peak week, trough week, seasonal amplitude by type
- Chart: `desc_seasonality_decomposition.png` — trend + seasonal components

### 4. Regional Distribution
- Use the `regional_comparison` skill to rank city-level regions by average price and by total volume
- Top 5 and bottom 5 regions for each metric
- Chart: `desc_top_regions_by_volume.png` — horizontal bar
- Chart: `desc_price_by_region_boxplot.png` — box plot

### 5. Product Mix
- Bag size proportions (small, large, xlarge) — national and by type
- Loose vs bagged ratio over time
- Chart: `desc_bag_size_mix.png`

### 6. Organic Premium
- Average organic premium (organic price - conventional price) nationally
- How has the premium changed over time?
- Chart: `desc_organic_premium_trend.png`

## Output Format

Write the report to `outputs/descriptive_report_YYYY-MM-DD.md` (using today's date).

Structure:
```markdown
# Descriptive Analysis — Avocado Sales
**Date:** YYYY-MM-DD
**Data source:** data/processed/avocado_features.csv
**Regions analyzed:** city-level only (N regions)
**Date range:** [first date] to [last date]

## Key Findings
- [3-5 bullet points — the most important patterns]

## 1. Price Trends
[analysis + chart references]

## 2. Volume Trends
...

## 6. Organic Premium
...
```

## Rules

1. **City-level only.** Filter to `region_level == "city"` for all analysis. Never include TotalUS, West, Southeast, or other aggregates.
2. **Cite every number.** Every statistic must reference the column and filter that produced it. Example: "Mean conventional price was $1.16 (avocado_features.csv, AveragePrice where type='conventional', all city-level regions, 2015-2018)."
3. **Do not interpret causation.** This is descriptive — report what happened, not why. Flag interesting patterns for the diagnostic agent to investigate.
4. **Save all charts** via the `chart_generator` skill with the `desc_` prefix.
