"""Add date-derived columns from Date column."""

import pandas as pd

from ..columns import find_column_by_pattern


def add_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add Year, Quarter, Day, MonthName, Date (For Trendline) from Date column."""
    date_col = find_column_by_pattern(df, r"^date$")
    if date_col is None:
        return df
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], format="mixed", errors="coerce")
    df["Year"] = df[date_col].dt.year
    df["Quarter"] = df[date_col].dt.quarter
    df["Day"] = df[date_col].dt.day
    df["MonthName"] = df[date_col].dt.strftime("%b")
    df["Date (For Trendline)"] = df[date_col].dt.strftime("%d-%b-%Y")
    return df
