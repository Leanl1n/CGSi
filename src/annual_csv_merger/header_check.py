"""Check if CSV/Excel files have headers that match canonical output columns (case-insensitive)."""

import pandas as pd

try:
    from ..reader import load_table
except ImportError:
    from reader import load_table

try:
    from ..constants import CANONICAL_OUTPUT_COLUMNS
except ImportError:
    from constants import CANONICAL_OUTPUT_COLUMNS

_CANONICAL_LOWER = {c.strip().lower() for c in CANONICAL_OUTPUT_COLUMNS}


def get_headers(path: str) -> list[str] | None:
    """
    Read only the header row of a CSV or Excel file (uses src.reader.load_table).
    Returns list of column names or None on failure.
    """
    try:
        df = load_table(path)
        return list(df.columns) if df is not None and not df.empty else None
    except Exception:
        return None


def map_columns_to_canonical(source_columns: list[str]) -> dict[str, str]:
    """
    Map source column names to canonical names (case-insensitive match).
    Returns dict: canonical_name -> source_column_name (first match per canonical).
    """
    canonical_to_source: dict[str, str] = {}
    source_lower_to_original: dict[str, str] = {c.strip().lower(): c for c in source_columns}
    for canon in CANONICAL_OUTPUT_COLUMNS:
        key = canon.strip().lower()
        if key in source_lower_to_original:
            canonical_to_source[canon] = source_lower_to_original[key]
    return canonical_to_source


def file_has_matching_headers(headers: list[str] | None) -> bool:
    """Return True if at least one header matches a canonical column (case-insensitive)."""
    if not headers:
        return False
    lower_headers = {h.strip().lower() for h in headers}
    return bool(lower_headers & _CANONICAL_LOWER)


def file_has_all_canonical_headers(headers: list[str] | None) -> bool:
    """Return True only if every canonical column is present (case-insensitive)."""
    if not headers:
        return False
    lower_headers = {h.strip().lower() for h in headers}
    return _CANONICAL_LOWER <= lower_headers


def reorder_df_to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reorder and normalize columns so the dataframe has exactly CANONICAL_OUTPUT_COLUMNS
    in canonical order. Source columns are matched case-insensitively; missing
    canonical columns are added as NaN. Non-canonical columns are dropped.
    """
    canonical_to_source = map_columns_to_canonical(list(df.columns))
    out = pd.DataFrame(index=df.index)
    for col in CANONICAL_OUTPUT_COLUMNS:
        if col in canonical_to_source:
            src = canonical_to_source[col]
            out[col] = df[src].values
        else:
            out[col] = pd.NA
    return out


def headers_align(paths: list[str]) -> tuple[bool, list[list[str] | None], list[str] | None]:
    """
    Check if all files have readable headers and every file has all canonical
    output columns (case-insensitive). Column order does not matter.
    Returns (aligned, list_of_headers_per_file, reference_header).
    reference_header is the canonical output column list when aligned.
    """
    if not paths:
        return False, [], None

    all_headers: list[list[str] | None] = []
    for path in paths:
        h = get_headers(path)
        all_headers.append(h)
        if h is None:
            return False, all_headers, None
        if not file_has_all_canonical_headers(h):
            return False, all_headers, None
    return True, all_headers, CANONICAL_OUTPUT_COLUMNS
