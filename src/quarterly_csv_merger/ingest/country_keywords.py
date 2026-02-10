"""Country keyword detection and per-file processing."""

import os
import re
import pandas as pd

from .._deps import KEYWORDS, load_table
from ..columns import get_name_column


def keyword_from_filename(filename: str) -> str | None:
    """Extract country keyword from filename."""
    upper = filename.upper()
    for code in KEYWORDS:
        if upper.startswith(code + "_") or upper.startswith(code + "-"):
            return code
        if f"_{code}_" in upper or f"-{code}-" in upper:
            return code
    return None


def row_matches_keyword(row, name_col: str | None, file_keyword: str | None) -> str | None:
    """Return country code from row name if present, else file_keyword."""
    if name_col and name_col in row.index:
        val = row.get(name_col)
        if pd.notna(val) and isinstance(val, str):
            val_upper = val.upper()
            for code in KEYWORDS:
                if re.search(r"(?:^|[\s,])" + re.escape(code) + r"[\s_\-]", val_upper):
                    return code
    return file_keyword


def process_file(path: str, base_dir: str | None = None) -> pd.DataFrame:
    """Load file and add Country column from filename or name column."""
    df = load_table(path)
    if df.empty:
        return df

    name_col = get_name_column(df)
    file_keyword = keyword_from_filename(os.path.basename(path))

    countries = []
    for _, row in df.iterrows():
        kw = row_matches_keyword(row, name_col, file_keyword)
        if kw and kw in KEYWORDS:
            countries.append(KEYWORDS[kw])
        elif file_keyword and file_keyword in KEYWORDS:
            countries.append(KEYWORDS[file_keyword])
        else:
            countries.append("")

    df = df.copy()
    df["Country"] = countries
    df = df[df["Country"] != ""]
    return df


def collect_files(path: str) -> list[str]:
    """Return CSV/Excel paths from given file or directory."""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return []

    if os.path.isfile(path):
        lower = path.lower()
        if lower.endswith((".csv", ".xlsx", ".xls")):
            return [path]
        return []

    files = []
    for name in os.listdir(path):
        full = os.path.join(path, name)
        if not os.path.isfile(full):
            continue
        lower = name.lower()
        if lower.endswith((".csv", ".xlsx", ".xls")):
            if keyword_from_filename(name) is not None:
                files.append(full)
    return sorted(files)
