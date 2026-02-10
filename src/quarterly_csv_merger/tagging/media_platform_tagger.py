"""Tag Media Platform and Media Type from source and influencer."""

import re
import pandas as pd

from .._deps import MEDIA_PLATFORM_SOCIAL, OWNED_ACCOUNTS
from ..columns import find_column_by_pattern

_owned_regex: re.Pattern | None = None


def _get_source_tag_patterns() -> list[tuple[re.Pattern, str]]:
    """Return compiled regex patterns for source to Media Platform."""
    return [
        (re.compile(re.escape(tag), re.IGNORECASE), tag)
        for tag in MEDIA_PLATFORM_SOCIAL.values()
    ]


def tag_source_by_regex(value) -> str:
    """Tag source value as Facebook, Instagram, Twitter, or News."""
    if pd.isna(value):
        return "News"
    s = str(value).strip()
    if not s:
        return "News"
    for pattern, tag in _get_source_tag_patterns():
        if pattern.search(s):
            return tag
    return "News"


def _normalize_handle(s: str) -> str:
    """Normalize handle for owned-account matching."""
    if pd.isna(s) or not isinstance(s, str):
        return ""
    return str(s).strip().lower().lstrip("@").replace(".", "").replace("_", "")


def _get_owned_regex() -> re.Pattern:
    """Return compiled regex for owned-account match (cached)."""
    global _owned_regex
    if _owned_regex is None:
        normalized = [_normalize_handle(x) for x in OWNED_ACCOUNTS if _normalize_handle(x)]
        _owned_regex = re.compile(
            "^(?:" + "|".join(re.escape(n) for n in normalized) + ")$",
            re.IGNORECASE,
        )
    return _owned_regex


def is_owned_influencer(value) -> bool:
    """Return True if influencer matches owned accounts."""
    norm = _normalize_handle(value) if pd.notna(value) else ""
    return bool(norm and _get_owned_regex().fullmatch(norm))


def match_media_platform_as_news(platform_value) -> bool:
    """Return True if platform value indicates News."""
    if pd.isna(platform_value):
        return False
    return bool(re.search(r"news", str(platform_value).strip(), re.IGNORECASE))


def match_media_platform_as_social(platform_value) -> bool:
    """Return True if platform value indicates social (FB/IG/Twitter)."""
    if pd.isna(platform_value):
        return False
    pattern = "|".join(re.escape(tag) for tag in MEDIA_PLATFORM_SOCIAL.values())
    return bool(re.search(pattern, str(platform_value).strip(), re.IGNORECASE))


def add_media_platform_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add Media Platform column from Source (Facebook/Instagram/Twitter/News)."""
    source_col = find_column_by_pattern(df, r"source")
    if source_col is None:
        df = df.copy()
        df["Media Platform"] = "News"
        return df
    df = df.copy()
    df["Media Platform"] = df[source_col].map(tag_source_by_regex)
    return df


def add_media_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add Media Type from Media Platform and Influencer (Owned/Earned/News)."""
    media_platform_col = find_column_by_pattern(df, r"media\s*platform")
    if media_platform_col is None:
        df = df.copy()
        df["Media Type"] = "Earned"
        return df

    influencer_col = find_column_by_pattern(df, r"influencer")

    def tag_media_type(row) -> str:
        platform = row.get(media_platform_col)
        if pd.isna(platform):
            return "Earned"
        if match_media_platform_as_news(platform):
            return "News"
        if match_media_platform_as_social(platform):
            if influencer_col and influencer_col in row.index:
                if is_owned_influencer(row.get(influencer_col)):
                    return "Owned"
            return "Earned"
        return "News"

    df = df.copy()
    df["Media Type"] = df.apply(tag_media_type, axis=1)
    return df
