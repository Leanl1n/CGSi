"""Detect CSV/Excel file encoding (UTF-8, UTF-16, etc.)."""

try:
    from ..constants import COMMON_ENCODINGS
except ImportError:
    from constants import COMMON_ENCODINGS


def detect_encoding_from_bom(path: str) -> str | None:
    """Detect encoding from BOM (first few bytes). Returns None if no BOM."""
    try:
        with open(path, "rb") as f:
            raw = f.read(4)
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        if raw.startswith(b"\xff\xfe\x00\x00"):
            return "utf-32-le"
        if raw.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32-be"
        if raw.startswith(b"\xff\xfe"):
            return "utf-16-le"
        if raw.startswith(b"\xfe\xff"):
            return "utf-16-be"
        return None
    except Exception:
        return None


def detect_csv_encoding(path: str, sample_size: int = 65536) -> tuple[str, float]:
    """
    Detect encoding of a text/CSV file. Tries BOM first, then common encodings.
    Returns (encoding_name, confidence 0–1). For CSV we also need to decode without error.
    """
    path_lower = path.lower()
    if not path_lower.endswith(".csv"):
        return "utf-8", 0.5

    bom_enc = detect_encoding_from_bom(path)
    if bom_enc:
        return bom_enc, 1.0

    try:
        with open(path, "rb") as f:
            raw = f.read(sample_size)
    except Exception:
        return "utf-8", 0.0

    encodings_to_try = [
        "utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"
    ] + [e for e in COMMON_ENCODINGS if e not in ("utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be")]
    for enc in encodings_to_try:
        try:
            text = raw.decode(enc)
            if enc.startswith("utf-16") or enc.startswith("utf-32"):
                return enc, 0.9
            return enc, 0.85
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8", 0.0
