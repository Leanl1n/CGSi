"""Tag Market column from name column."""

import re
import pandas as pd

from .._deps import MARKET_BY_CODE
from ..columns import get_name_column


def tag_market_by_regex(name_value) -> str:
    """Return market name from name value via regex, or 'Unknown'."""
    if pd.isna(name_value) or not isinstance(name_value, str):
        return "Unknown"
    s = str(name_value).strip()
    if not s:
        return "Unknown"
    for code, market in MARKET_BY_CODE.items():
        pattern = r"(?:^|[\s,_\-])" + re.escape(code) + r"(?:$|[\s,_\-])"
        if re.search(pattern, s, re.IGNORECASE):
            return market
    return "Unknown"


def add_market_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add Market column from name column."""
    name_col = get_name_column(df)
    if name_col is None:
        df = df.copy()
        df["Market"] = "Unknown"
        return df
    df = df.copy()
    df["Market"] = df[name_col].map(tag_market_by_regex)
    return df
