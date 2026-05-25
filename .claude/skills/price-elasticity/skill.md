# Price Elasticity

Computes point price elasticity of demand via log-log OLS regression of volume on price, segmented by region and type.

## Trigger

Fires when an agent needs to quantify how volume responds to price changes — in diagnostic context (explaining volume swings) or prescriptive context (optimizing price for revenue).

## Instructions

When asked to compute price elasticity:

1. **Log-log OLS regression:**
   ```python
   import numpy as np
   import statsmodels.api as sm

   # For each (region, type) group:
   log_price = np.log(group["AveragePrice"])
   log_volume = np.log(group["Total Volume"])
   X = sm.add_constant(log_price)
   model = sm.OLS(log_volume, X).fit()
   elasticity = model.params[1]  # coefficient on log(price)
   ```

2. **Interpretation of elasticity coefficient:**
   - |e| > 1 → elastic (volume drops more than proportionally when price rises)
   - |e| < 1 → inelastic (volume is relatively insensitive to price)
   - |e| ≈ 1 → unit elastic
   - Expected sign is negative (price up → volume down)

3. **Group by region and type.** Compute separate elasticity for each (region, type) pair. Filter to `region_level == "city"` by default.

4. **Report for each group:**
   - Elasticity coefficient (B1)
   - Standard error
   - R-squared
   - p-value for the coefficient
   - 95% confidence interval
   - Interpretation flag: "elastic", "inelastic", or "unit_elastic"
   - Number of observations used

5. **Quality checks:**
   - Skip groups with fewer than 30 observations
   - Flag groups where R-squared < 0.05 (price explains almost no volume variance)
   - Flag groups where the elasticity sign is positive (unexpected — may indicate omitted variable bias or supply-side effects)

6. **Output format:**
   ```
   | region | type | elasticity | std_err | r_squared | p_value | ci_lower | ci_upper | interpretation | n_obs |
   ```

7. **Always cite** the data file, columns used (`AveragePrice`, `Total Volume`), and filter conditions in any report that uses these results.

8. **Caveat in reports:** Price elasticity from observational data reflects correlation, not causal impact. Supply shifts, seasonality, and regional factors confound the estimate. State this limitation when reporting.
