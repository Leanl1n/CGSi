"""Remove rows with blank URL column."""

import pandas as pd

from ..columns import find_column_by_pattern


def drop_blank_url_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where URL column is missing or empty."""
    url_col = find_column_by_pattern(df, r"url")
    if url_col is None:
        return df
    mask = df[url_col].notna() & (df[url_col].astype(str).str.strip() != "")
    return df.loc[mask].reset_index(drop=True)
