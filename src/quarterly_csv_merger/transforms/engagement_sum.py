"""Set Engagement column from sum of engagement-related columns."""

import pandas as pd

from .._deps import ENGAGEMENT_COLS
from ..columns import find_columns_by_patterns


def set_engagement_from_sum(df: pd.DataFrame) -> pd.DataFrame:
    """Sum engagement columns per row and set Engagement column."""
    found = find_columns_by_patterns(df, ENGAGEMENT_COLS)
    if not found:
        df = df.copy()
        if "Engagement" not in df.columns:
            df["Engagement"] = 0
        return df
    df = df.copy()
    engagement_sum = df[found].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    df["Engagement"] = engagement_sum.astype("int64")
    return df
