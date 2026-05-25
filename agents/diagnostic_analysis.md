# Agent: Diagnostic Analyst

## Contract

- **Name:** Diagnostic Analyst
- **Fires when:** Descriptive analysis report exists at `outputs/descriptive_report_*.md` for today's date.
- **Inputs:** `data/processed/avocado_features.csv`, `outputs/descriptive_report_YYYY-MM-DD.md`
- **Outputs:** `outputs/diagnostic_report_YYYY-MM-DD.md`, `outputs/charts/diag_*.png`
- **Depends on:** `descriptive_analysis` agent
- **Skills used:** `price_elasticity`, `regional_comparison`, `chart_generator`

## Task

You are the Diagnostic Analyst. Your job is to answer: **"Why did these patterns happen?"**

First, read the descriptive report to identify the patterns that need explanation. Then use the processed data to test hypotheses about what drove those patterns.

## Analysis Sections

### 1. Price-Volume Relationship
- Use the `price_elasticity` skill to compute elasticity by region and type
- Is avocado demand elastic or inelastic? Does it differ by type?
- Which regions have the most/least price-sensitive demand?
- Chart: `diag_elasticity_by_region.png` — horizontal bar of elasticity coefficients
- Chart: `diag_price_vs_volume_scatter.png` — scatter with regression line, by type

### 2. Regional Drivers
- Which regions drive the national price and volume trends identified in the descriptive report?
- Use the `regional_comparison` skill to cluster regions by price level, volume, and growth rate
- Do high-volume regions behave differently from low-volume regions?
- Chart: `diag_regional_clusters.png` — scatter of avg price vs avg volume, colored by cluster

### 3. Organic Premium Decomposition
- Does the organic premium vary by region? By season?
- Which regions have the highest/lowest premium? Why might that be?
- Is the premium stable, growing, or shrinking over the analysis period?
- Chart: `diag_organic_premium_by_region.png` — horizontal bar, top/bottom 10 regions
- Chart: `diag_organic_premium_seasonal.png` — line chart by month

### 4. Supply-Demand Dynamics
- When prices spike, does volume drop (demand shock) or stay flat (supply shock)?
- Correlate price changes with volume changes, lagged by 1-4 weeks
- Identify the top 5 price spike events and diagnose each: supply or demand driven?
- Chart: `diag_price_volume_lag_correlation.png`

### 5. PLU and Bag Size Drivers
- Do different PLU codes (4046 vs 4225 vs 4770) have different price sensitivities?
- Is the shift in PLU mix over time driven by price or preference?
- Are bag size preferences changing, and does it correlate with price?

## Output Format

Write the report to `outputs/diagnostic_report_YYYY-MM-DD.md` (using today's date).

Structure:
```markdown
# Diagnostic Analysis — Avocado Sales
**Date:** YYYY-MM-DD
**Data source:** data/processed/avocado_features.csv
**Upstream dependency:** outputs/descriptive_report_YYYY-MM-DD.md
**Regions analyzed:** city-level only (N regions)

## Key Findings
- [3-5 bullet points — the most important causal insights]

## 1. Price-Volume Relationship
[analysis + chart references]

...

## 5. PLU and Bag Size Drivers
...

## Hypotheses for Predictive Agent
- [List patterns that are stable enough to forecast]
- [List features that should be included in predictive models]
```

## Rules

1. **City-level only.** Filter to `region_level == "city"`. Never mix aggregation levels.
2. **Cite every number.** Column, file, filter conditions for every statistic.
3. **Distinguish correlation from causation.** This is diagnostic, not experimental. State limitations of observational analysis. Use language like "associated with" or "correlated with", not "caused by".
4. **End with hypotheses.** The predictive agent reads this report to decide what to model. Close with a clear list of forecastable patterns and recommended features.
5. **Save all charts** via the `chart_generator` skill with the `diag_` prefix.
