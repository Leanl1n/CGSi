"""Merge pipeline: ingest, clean, tag, transform, output."""

import os
from pathlib import Path
import pandas as pd

from ._deps import OUTPUT_DIR, OUTPUT_ENCODING, RAW_DATA_PATH
from .ingest import collect_files, process_file
from .cleaning import drop_blank_url_rows
from .tagging import (
    add_market_column,
    add_media_platform_column,
    add_media_type_column,
    add_brand_from_keywords,
)
from .transforms import add_date_columns, set_engagement_from_sum
from .columns import select_output_columns


def merge_data(input_path: str, base_dir: str | None = None) -> pd.DataFrame:
    """Load and merge CSV/Excel files by country keywords; return transformed DataFrame."""
    if base_dir is None:
        base_dir = str(Path(__file__).resolve().parent.parent.parent)
    if not input_path or not str(input_path).strip():
        return pd.DataFrame()
    path = input_path.strip()
    path = os.path.join(base_dir, path) if not os.path.isabs(path) else path

    files = collect_files(path)
    if not files:
        return pd.DataFrame()

    frames = []
    for f in files:
        try:
            df = process_file(f, base_dir=base_dir)
            if not df.empty:
                frames.append(df)
        except Exception as e:
            print(f"Warning: skipped {f}: {e}")

    if not frames:
        return pd.DataFrame()

    merged = pd.concat(frames, ignore_index=True)
    merged = drop_blank_url_rows(merged)
    merged = add_market_column(merged)
    merged = add_media_platform_column(merged)
    merged = add_media_type_column(merged)
    merged = add_date_columns(merged)
    merged = set_engagement_from_sum(merged)
    merged = add_brand_from_keywords(merged, base_dir=base_dir)
    return merged


def run_merge_and_save(
    input_path: str,
    base_dir: str | None = None,
    df: pd.DataFrame | None = None,
) -> Path | None:
    """Merge data (or use provided df), select output columns, save to output dir."""
    if base_dir is None:
        base_dir = str(Path(__file__).resolve().parent.parent.parent)
    if df is None:
        df = merge_data(input_path, base_dir=base_dir)
    if df.empty:
        return None
    out_df = select_output_columns(df)
    base = Path(base_dir)
    out_dir = base / OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "data.csv"
    out_df.to_csv(out_csv, index=False, encoding=OUTPUT_ENCODING)
    return out_csv


def main() -> None:
    """CLI entry: merge from path and save CSV."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Merge CSV/Excel by country keywords (ID, SG, TH, MY)."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=RAW_DATA_PATH,
        help=f"Input CSV/Excel file or folder (default: {RAW_DATA_PATH})",
    )
    args = parser.parse_args()
    base = Path(__file__).resolve().parent.parent.parent
    df = merge_data(args.input, base_dir=str(base))
    if df.empty:
        print("No data merged (no files or no rows matched keywords).")
        return
    out_csv = run_merge_and_save(args.input, base_dir=str(base), df=df)
    print(f"Merged DataFrame: {len(df)} rows.")
    print("\nRows per country:", df["Country"].value_counts().sort_index().to_dict())
    print(f"\nSaved: {out_csv}")
