"""Annual CSV Merger: encoding detection and header-aligned merge (direct, uses src.reader)."""

try:
    from ..constants import CANONICAL_OUTPUT_COLUMNS
except ImportError:
    from constants import CANONICAL_OUTPUT_COLUMNS
from .encoding import detect_csv_encoding, detect_encoding_from_bom
from .header_check import (
    file_has_all_canonical_headers,
    file_has_matching_headers,
    get_headers,
    headers_align,
    map_columns_to_canonical,
    reorder_df_to_canonical,
)
from .merge import load_file_with_encoding, merge_if_aligned

__all__ = [
    "CANONICAL_OUTPUT_COLUMNS",
    "detect_csv_encoding",
    "file_has_all_canonical_headers",
    "file_has_matching_headers",
    "detect_encoding_from_bom",
    "get_headers",
    "headers_align",
    "load_file_with_encoding",
    "map_columns_to_canonical",
    "merge_if_aligned",
    "reorder_df_to_canonical",
]
