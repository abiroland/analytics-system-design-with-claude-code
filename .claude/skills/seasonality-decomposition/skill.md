# Seasonality Decomposition

Performs STL decomposition on a specified numeric column, grouped by region and type. Isolates trend, seasonal, and residual components.

## Trigger

Fires when an agent needs to isolate seasonal patterns from trend — specifically when analyzing time series behavior (descriptive agent) or preparing features for forecasting (predictive agent).

## Instructions

When asked to decompose seasonality:

1. **Use statsmodels STL:**
   ```python
   from statsmodels.tsa.seasonal import STL

   stl = STL(series, period=52, robust=True)
   result = stl.fit()
   # result.trend, result.seasonal, result.resid
   ```

2. **Default period is 52** (weekly data, annual cycle). Override only if the caller specifies a different periodicity.

3. **Group the decomposition** by region and type. Do not decompose across groups — each (region, type) pair gets its own STL fit:
   ```python
   for (region, avocado_type), group in df.groupby(["region", "type"]):
       series = group.set_index("Date")["AveragePrice"]
       # ... run STL on this series
   ```

4. **Filter to city-level regions only** (`region_level == "city"`) unless the caller explicitly requests aggregates. This enforces invariant #1.

5. **Output columns:** Append `_trend`, `_seasonal`, `_residual` suffixes to the target column name. Example: decomposing `AveragePrice` produces `AveragePrice_trend`, `AveragePrice_seasonal`, `AveragePrice_residual`.

6. **Summary statistics to report:**
   - Seasonal amplitude (max - min of seasonal component) per group
   - Strength of seasonality: `1 - Var(residual) / Var(seasonal + residual)`
   - Peak week (week_of_year with highest seasonal value) per group

7. **Minimum series length:** STL requires at least 2 full periods (104 weeks). Skip groups with fewer observations and log a warning.

8. **Always cite** the source column and data file in any output that uses these results.
