# Chart Generator

Produces FT-styled, insight-driven charts with data-backed annotations.

**Companion skill:** Always apply the `chart_commentary` skill alongside this one. It defines the FT visual theme, annotation placement rules, and title standards. Every chart must follow both skills.

## Trigger

Fires whenever an agent needs to produce a visualization. All chart creation in this system routes through this skill for visual consistency.

## Instructions

When asked to create a chart:

1. **Apply the FT theme from `chart_commentary` skill.** Do not use seaborn default themes. The FT theme (cream background, teal/claret palette, horizontal-only gridlines) is the standard for all charts in this system.

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

4. **Title is the insight** (from `chart_commentary` skill):
   - Title states a quantified finding, not a description
   - Subtitle connects the finding to a business decision
   - No vague language, no causal claims the data can't support

5. **One annotation max** (from `chart_commentary` skill):
   - Arrow target coordinates read from data, not hardcoded
   - Mark target with a dot
   - Text placed in clear space — never on top of a data line
   - Content states specific date, value, or comparison

6. **Series labels:** Inline at end of each line, color-matched. No legend box.

7. **Source line:** Bottom-left, 8pt, citing file + columns + filters.

8. **Always** create the `outputs/charts/` directory before saving:
   ```python
   from pathlib import Path
   Path("outputs/charts").mkdir(parents=True, exist_ok=True)
   ```

9. **Return** the file path of the saved chart so the calling agent can embed it in its report.
