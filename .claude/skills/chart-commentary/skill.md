# Chart Commentary

Adds FT-style visual design and data-driven annotations to charts. Every chart produced by the chart_generator skill must follow these rules.

## Trigger

Fires alongside chart_generator on every chart. This skill governs the visual theme, annotation placement, and commentary standards.

## FT Visual Theme

Apply this configuration to every chart:

```python
FT_BG = '#FFF1E5'        # cream background
FT_TEXT = '#33302E'       # dark brown-grey
FT_GRID = '#E6D9CE'      # muted grid
FT_ACCENT1 = '#0D7680'   # teal (conventional / primary series)
FT_ACCENT2 = '#990F3D'   # claret (organic / secondary series)
FT_LINE_GREY = '#B3A89D'
FT_CALLOUT = '#66605C'   # subtitle and annotation text

plt.rcParams.update({
    'figure.facecolor': FT_BG, 'axes.facecolor': FT_BG,
    'axes.edgecolor': FT_GRID, 'axes.labelcolor': FT_TEXT,
    'text.color': FT_TEXT, 'xtick.color': FT_TEXT, 'ytick.color': FT_TEXT,
    'grid.color': FT_GRID, 'grid.linewidth': 0.6,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica'],
    'font.size': 11, 'figure.figsize': (12, 7), 'figure.dpi': 300,
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.3,
    'savefig.facecolor': FT_BG,
})
```

**Spines:** Remove top, right, and left. Keep bottom only, colored `FT_LINE_GREY`.

**Gridlines:** Horizontal only (`ax.yaxis.grid(True)`), no vertical (`ax.xaxis.grid(False)`).

**Series labels:** Inline at the end of each line, not a legend box. Color-match the label to the line.

**Source line:** Bottom-left, 8pt, color `#96908A`. Must cite file, columns, and filters used.

## Title Is the Insight

The chart title must state a finding, not describe the chart.

- **Wrong:** "Average Price by Type Over Time"
- **Wrong:** "Price Trends — Conventional vs Organic"
- **Right:** "Conventional prices are 60% more volatile than organic"

The subtitle (one line, `FT_CALLOUT` color) gives leadership the *so what* — why this finding matters for a business decision.

- **Wrong:** "The gap narrows when conventional spikes and widens when it drops"
- **Right:** "Organic pricing is more predictable — a strategic advantage for supply planning"

### Rules for Titles and Subtitles

1. Lead with a quantified fact. Use numbers, percentages, dollar amounts.
2. Do not use vague language: "moves together," "acts as," "associated with." State the specific relationship the data shows.
3. Do not invent mechanisms or causal claims the data cannot support. If you don't know *why*, don't guess. State *what*.
4. Subtitle must connect the finding to a business action or decision. If it doesn't help leadership do something, cut it.

## Annotations

Each chart gets **at most one annotation**. Its job is to anchor the title's claim to a specific moment in the data.

### Placement Rules

1. **Arrow target (`xy`) must be read from the data**, not hardcoded. Look up the actual value:
   ```python
   target_date = pd.Timestamp('2017-03-26')
   y_value = series.loc[series['Date'] == target_date, column].values[0]
   ax.annotate(..., xy=(target_date, y_value), ...)
   ```
2. **Mark the target** with a dot (`ax.plot(date, value, 'o', ...)`) so the reader sees exactly what the arrow points at.
3. **Text box (`xytext`) must sit in clear space** — no overlap with any data line, axis label, or other text. Before placing:
   - Check the y-range of data near the text x-position
   - Place the text above the highest data point in that region, or in empty margin space
   - If needed, extend the axis limits (`ax.set_xlim`, `ax.set_ylim`) to create room
4. **Never place annotation text on top of a data line.** If there is no clear space near the target, move the text further away — a longer arrow is better than overlapping text.

### Content Rules

1. State the specific date, value, or comparison. "Mar 2017: conventional surges to within $0.15 of organic" — not "prices converge."
2. All numbers in the annotation must come from the data. Verify before writing.
3. Do not add a second annotation. If there are two findings, the second goes in the report text, not the chart.

## What Not to Do

These are mistakes made during development of this system. Do not repeat them.

1. **Do not add multiple arrows pointing at different parts of the chart.** The eye doesn't know where to go. One annotation per chart.
2. **Do not call something a "price floor" unless it literally cannot go below that level.** Lower volatility is not a floor.
3. **Do not hardcode annotation coordinates.** If the data changes, hardcoded positions will point at the wrong spot. Always read from the DataFrame.
4. **Do not use language like "acts as," "suggests," "appears to" in titles.** Titles state facts. Caveats go in the report.
5. **Do not place annotation text at a y-position between the two series lines.** It will overlap one of them.
