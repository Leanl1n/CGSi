"""Combine CSV/Excel files when headers align. Uses src.reader (direct load, no quarterly logic)."""

from __future__ import annotations

from typing import Callable

import pandas as pd

try:
    from ..reader import load_table
except ImportError:
    from reader import load_table

from .encoding import detect_csv_encoding
from .header_check import headers_align, reorder_df_to_canonical


def load_file_with_encoding(path: str) -> tuple[pd.DataFrame | None, str, float]:
    """
    Load CSV or Excel via src.reader.load_table; return (df, encoding_label, confidence).
    Encoding is only meaningful for CSV; for Excel returns ('excel', 1.0).
    """
    try:
        df = load_table(path)
    except Exception:
        return None, "unknown", 0.0
    if df is None:
        return None, "unknown", 0.0
    if path.lower().endswith(".csv"):
        enc, confidence = detect_csv_encoding(path)
        return df, enc, confidence
    return df, "excel", 1.0


def merge_if_aligned(
    paths: list[str],
    progress_callback: Callable[[float, str], None] | None = None,
) -> tuple[pd.DataFrame | None, list[dict], bool]:
    """
    If all files have aligned headers, load and concatenate them (direct: src.reader only).
    Returns (merged_dataframe, report_list, headers_aligned).
    report_list contains per-file: path, encoding, confidence, rows, columns.
    progress_callback(progress_ratio, message) is called to report progress (0.0 to 1.0).
    """
    n = len(paths)
    total_steps = max(1, n * 2 + 2)  # headers + load each + load each for frames + combine

    def report_step(step: int, msg: str) -> None:
        if progress_callback is not None:
            progress_callback(step / total_steps, msg)

    report_step(0, "Checking headers...")
    aligned, all_headers, ref_header = headers_align(paths)
    report: list[dict] = []
    step = 1

    for i, path in enumerate(paths):
        report_step(step, f"Loading file {i + 1} of {n}...")
        step += 1
        df, enc, confidence = load_file_with_encoding(path)
        if df is None:
            report.append({
                "path": path,
                "encoding": enc,
                "confidence": confidence,
                "rows": 0,
                "columns": [],
                "error": "Could not read file",
            })
            continue
        report.append({
            "path": path,
            "encoding": enc,
            "confidence": confidence,
            "rows": len(df),
            "columns": list(df.columns),
        })

    if not aligned:
        return None, report, False

    frames: list[pd.DataFrame] = []
    for i, path in enumerate(paths):
        report_step(step, f"Reading file {i + 1} of {n}...")
        step += 1
        df, _, _ = load_file_with_encoding(path)
        if df is not None and not df.empty:
            # Ensure each file has columns in canonical order (same schema for merge).
            df = reorder_df_to_canonical(df)
            frames.append(df)

    report_step(step, "Combining...")
    step += 1

    if not frames:
        report_step(total_steps, "Done.")
        return None, report, True

    merged = pd.concat(frames, ignore_index=True)
    report_step(total_steps, "Done.")
    return merged, report, True
