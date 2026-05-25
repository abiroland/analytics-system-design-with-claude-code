# Regional Comparison

Ranks regions on a specified metric and optionally clusters them using k-means on standardized features.

## Trigger

Fires when an agent needs to compare regions — identifying top/bottom performers, grouping similar markets, or finding outliers.

## Instructions

When asked to compare regions:

1. **Always filter to city-level regions** (`region_level == "city"`) by default. Aggregate regions (TotalUS, West, Southeast, etc.) must be excluded to avoid double-counting. Only include aggregates if the caller explicitly requests them and the analysis is specifically about aggregate-level patterns.

2. **Ranking:**
   ```python
   # Compute metric per region (e.g., mean AveragePrice)
   ranked = (
       df[df["region_level"] == "city"]
       .groupby("region")[metric_col]
       .agg(["mean", "std", "min", "max"])
       .sort_values("mean", ascending=False)
   )
   ranked["percentile"] = ranked["mean"].rank(pct=True)
   ```

3. **Clustering** (when requested):
   ```python
   from sklearn.preprocessing import StandardScaler
   from sklearn.cluster import KMeans

   scaler = StandardScaler()
   X_scaled = scaler.fit_transform(region_features)
   kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
   clusters = kmeans.fit_predict(X_scaled)
   ```
   - Default `n_clusters=4` unless caller specifies otherwise
   - Always set `random_state=42` for reproducibility
   - Report cluster centroids in original (unscaled) units

4. **Outlier detection:** Flag any region more than 2 standard deviations from its cluster centroid. Report these separately.

5. **Output format:**
   - Ranked table: region, metric mean, metric std, percentile rank
   - If clustered: cluster assignment, distance to centroid, outlier flag
   - Top 5 and bottom 5 regions highlighted

6. **Always cite** which metric column, data file, and filter conditions produced the ranking.
