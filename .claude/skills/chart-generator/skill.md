# Chart Generator

Produces publication-quality matplotlib/seaborn charts with consistent styling.

## Trigger

Fires whenever an agent needs to produce a visualization. All chart creation in this system routes through this skill for visual consistency.

## Instructions

When asked to create a chart:

1. **Use this standard style setup** at the top of every chart script:
   ```python
   import matplotlib.pyplot as plt
   import seaborn as sns

   sns.set_theme(style="whitegrid", font_scale=1.1)
   plt.rcParams.update({
       "figure.figsize": (10, 6),
       "figure.dpi": 300,
       "axes.titlesize": 14,
       "axes.labelsize": 12,
       "legend.fontsize": 10,
       "savefig.bbox": "tight",
       "savefig.pad_inches": 0.2,
   })
   ```

2. **Chart types available:** line, bar, heatmap, scatter, box. Choose based on what the data shows:
   - Time series → line chart
   - Category comparison → horizontal bar
   - Correlation matrix → heatmap
   - Relationship between two variables → scatter
   - Distribution across groups → box plot

3. **Naming convention:** Save all charts to `outputs/charts/` with prefix indicating the agent:
   - `desc_` for descriptive analysis
   - `diag_` for diagnostic analysis
   - `pred_` for predictive analysis
   - `presc_` for prescriptive analysis
   - Example: `outputs/charts/desc_price_trend_by_type.png`

4. **Required elements on every chart:**
   - Descriptive title (what the chart shows, not just variable names)
   - Labeled axes with units where applicable (e.g., "Average Price ($)")
   - Legend if multiple series
   - No chartjunk — remove unnecessary gridlines, borders, decorations

5. **Color palette:** Use `sns.color_palette("husl", n)` for categorical data, `sns.color_palette("coolwarm", n)` for diverging data. Use consistent colors for conventional (blue) and organic (green) throughout all charts.

6. **Always** create the `outputs/charts/` directory before saving:
   ```python
   from pathlib import Path
   Path("outputs/charts").mkdir(parents=True, exist_ok=True)
   ```

7. **Return** the file path of the saved chart so the calling agent can embed it in its report.
