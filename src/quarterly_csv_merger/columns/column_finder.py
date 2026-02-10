"""Column discovery by pattern and output column selection."""

import re
import pandas as pd

from .._deps import NAME_COLUMN_CANDIDATES, OUTPUT_CSV_COLUMNS


def get_name_column(df: pd.DataFrame) -> str | None:
    """Return first existing name column for keyword search."""
    for col in NAME_COLUMN_CANDIDATES:
        if col in df.columns:
            return col
    return None


def find_column_by_pattern(df: pd.DataFrame, pattern: str) -> str | None:
    """Return first column matching pattern (case-insensitive), or None."""
    for col in df.columns:
        if re.search(pattern, str(col), re.IGNORECASE):
            return col
    return None


def find_columns_by_patterns(df: pd.DataFrame, names: list[str]) -> list[str]:
    """Return columns matching any of the given names (whole-word, case-insensitive)."""
    if not names:
        return []
    pattern = re.compile(
        r"^(?:" + "|".join(re.escape(n) for n in names) + r")$",
        re.IGNORECASE,
    )
    return [col for col in df.columns if pattern.search(str(col).strip())]


def build_keywords_dict(df: pd.DataFrame) -> tuple[dict[int, list[str]], str | None]:
    """Find keyword column and return (row_index -> keyword list, column name or None)."""
    keyword_col = find_column_by_pattern(df, r"keyword")
    if keyword_col is None:
        return {}, None
    d: dict[int, list[str]] = {}
    for i, val in df[keyword_col].items():
        if pd.isna(val) or not isinstance(val, str):
            d[i] = []
        else:
            parts = [s.strip() for s in str(val).split(",") if s.strip()]
            d[i] = parts
    return d, keyword_col


def _col_or_none(df: pd.DataFrame, *candidates: str) -> str | None:
    """Return first existing column from candidates, or None."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def select_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame with only output columns, mapping from existing where needed."""
    out = pd.DataFrame(index=df.index)
    brand_col = _col_or_none(df, "Brand")

    for col in OUTPUT_CSV_COLUMNS:
        if col in df.columns:
            out[col] = df[col]
        elif col == "Brand" and brand_col:
            out[col] = df[brand_col]
        elif col == "Brand":
            out[col] = ""
        else:
            out[col] = ""
    return out[list(OUTPUT_CSV_COLUMNS)]
