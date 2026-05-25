"""
Avocado Sales Data Pipeline
============================
Reads raw avocado.csv, cleans it, classifies regions, engineers features,
and writes two outputs:
  - data/processed/avocado_clean.csv   (cleaned, no new features)
  - data/processed/avocado_features.csv (with engineered features)

Usage:
    python src/data_prep.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "avocado.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# ---------------------------------------------------------------------------
# Region classification
# ---------------------------------------------------------------------------
AGGREGATE_REGIONS = {
    "TotalUS",
    "West",
    "Northeast",
    "Southeast",
    "SouthCentral",
    "Midsouth",
    "GreatLakes",
    "Plains",
}

STATE_REGIONS = {
    "California",
    "SouthCarolina",
    "NorthernNewEngland",
    "WestTexNewMexico",
}

# Everything else is city-level.


def classify_region(region: str) -> str:
    """Assign region_level: 'aggregate', 'state', or 'city'."""
    if region in AGGREGATE_REGIONS:
        return "aggregate"
    if region in STATE_REGIONS:
        return "state"
    return "city"


def load_and_clean(path: Path) -> pd.DataFrame:
    """
    Load raw CSV, drop redundant index, parse dates, classify regions.

    Parameters
    ----------
    path : Path
        Path to raw avocado.csv.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe with proper dtypes and region_level column.
    """
    df = pd.read_csv(path)

    # Drop unnamed index column
    if df.columns[0] == "" or df.columns[0].startswith("Unnamed"):
        df = df.drop(columns=df.columns[0])

    # Parse dates (DD/MM/YYYY)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

    # Sort by date and region for consistent ordering
    df = df.sort_values(["region", "type", "Date"]).reset_index(drop=True)

    # Classify regions
    df["region_level"] = df["region"].map(classify_region)

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns for analysis.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned avocado dataframe from load_and_clean().

    Returns
    -------
    pd.DataFrame
        DataFrame with engineered feature columns appended.

    Features Engineered
    -------------------
    - Temporal: week_of_year, month, quarter
    - Volume shares: plu_4046_share, plu_4225_share, plu_4770_share
    - Bag proportions: small_bag_pct, large_bag_pct, xlarge_bag_pct
    - Organic premium: price difference (organic - conventional) for same
      date and region
    - YoY lag: AveragePrice from 52 weeks prior (same region/type)
    """
    feat = df.copy()

    # --- Temporal features ---
    feat["week_of_year"] = feat["Date"].dt.isocalendar().week.astype(int)
    feat["month"] = feat["Date"].dt.month
    feat["quarter"] = feat["Date"].dt.quarter

    # --- Volume shares by PLU ---
    total_vol = feat["Total Volume"].replace(0, np.nan)
    feat["plu_4046_share"] = feat["4046"] / total_vol
    feat["plu_4225_share"] = feat["4225"] / total_vol
    feat["plu_4770_share"] = feat["4770"] / total_vol

    # --- Bag size proportions ---
    total_bags = feat["Total Bags"].replace(0, np.nan)
    feat["small_bag_pct"] = feat["Small Bags"] / total_bags
    feat["large_bag_pct"] = feat["Large Bags"] / total_bags
    feat["xlarge_bag_pct"] = feat["XLarge Bags"] / total_bags

    # --- Organic price premium ---
    price_pivot = feat.pivot_table(
        index=["Date", "region"],
        columns="type",
        values="AveragePrice",
    )
    if "organic" in price_pivot.columns and "conventional" in price_pivot.columns:
        price_pivot["organic_premium"] = (
            price_pivot["organic"] - price_pivot["conventional"]
        )
        premium = price_pivot["organic_premium"].reset_index()
        feat = feat.merge(premium, on=["Date", "region"], how="left")
    else:
        feat["organic_premium"] = np.nan

    # --- YoY price lag (52-week lag within same region + type) ---
    feat = feat.sort_values(["region", "type", "Date"])
    feat["price_yoy_lag"] = feat.groupby(["region", "type"])["AveragePrice"].shift(52)

    feat = feat.reset_index(drop=True)
    return feat


def main() -> None:
    """Run the full pipeline."""
    print(f"Reading raw data from {RAW_PATH}")
    df_clean = load_and_clean(RAW_PATH)

    region_counts = df_clean.groupby("region_level")["region"].nunique()
    print(f"  Rows: {len(df_clean):,}")
    print(f"  Date range: {df_clean['Date'].min().date()} to {df_clean['Date'].max().date()}")
    print(f"  Regions: {df_clean['region'].nunique()} "
          f"(city={region_counts.get('city', 0)}, "
          f"state={region_counts.get('state', 0)}, "
          f"aggregate={region_counts.get('aggregate', 0)})")

    # Write clean version
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    clean_path = PROCESSED_DIR / "avocado_clean.csv"
    df_clean.to_csv(clean_path, index=False)
    print(f"\nWrote cleaned data to {clean_path}")

    # Engineer features and write
    print("Engineering features...")
    df_feat = engineer_features(df_clean)
    feat_path = PROCESSED_DIR / "avocado_features.csv"
    df_feat.to_csv(feat_path, index=False)
    print(f"Wrote feature data to {feat_path}")
    print(f"  Columns: {list(df_feat.columns)}")
    print(f"  Shape: {df_feat.shape}")


if __name__ == "__main__":
    main()
