"""Resolve constants and reader for package or script run."""

try:
    from ..constants import (
        BRAND_JSON_FILENAME,
        ENGAGEMENT_COLS,
        KEYWORDS,
        MARKET_BY_CODE,
        MEDIA_PLATFORM_SOCIAL,
        NAME_COLUMN_CANDIDATES,
        OUTPUT_CSV_COLUMNS,
        OUTPUT_DIR,
        OUTPUT_ENCODING,
        OWNED_ACCOUNTS,
        RAW_DATA_PATH,
    )
    from ..reader import load_table
except ImportError:
    from constants import (
        BRAND_JSON_FILENAME,
        ENGAGEMENT_COLS,
        KEYWORDS,
        MARKET_BY_CODE,
        MEDIA_PLATFORM_SOCIAL,
        NAME_COLUMN_CANDIDATES,
        OUTPUT_CSV_COLUMNS,
        OUTPUT_DIR,
        OUTPUT_ENCODING,
        OWNED_ACCOUNTS,
        RAW_DATA_PATH,
    )
    from reader import load_table
