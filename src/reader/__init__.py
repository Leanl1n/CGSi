"""CSV and Excel reading with encoding and separator handling."""

import pandas as pd


def detect_encoding(path: str) -> str:
    """Detect CSV encoding from BOM; default utf-8."""
    try:
        with open(path, "rb") as f:
            raw = f.read(4)
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            return "utf-16"
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        return "utf-8"
    except Exception:
        return "utf-8"


def read_csv(path: str) -> pd.DataFrame:
    """Read CSV with encoding and separator detection."""
    enc = detect_encoding(path)
    for sep in (",", "\t"):
        for encoding in (enc, "utf-8-sig", "utf-8", "latin-1", "cp1252"):
            try:
                df = pd.read_csv(path, sep=sep, encoding=encoding, low_memory=False)
                if df is not None and not (df.empty and len(df.columns) <= 1):
                    return df
            except Exception:
                continue
    try:
        return pd.read_csv(path, encoding="utf-8", low_memory=False, on_bad_lines="skip")
    except TypeError:
        try:
            return pd.read_csv(path, encoding="utf-8", low_memory=False)
        except Exception as e:
            raise RuntimeError(f"Could not read CSV: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Could not read CSV: {e}") from e


def read_excel(path: str) -> pd.DataFrame:
    """Read first sheet of Excel file (openpyxl or xlrd for .xls)."""
    path_lower = path.lower()
    errors = []
    if path_lower.endswith(".xls"):
        try:
            return pd.read_excel(path, engine="xlrd")
        except Exception as e:
            errors.append(f"xlrd: {e}")
    try:
        return pd.read_excel(path, engine="openpyxl")
    except Exception as e:
        errors.append(f"openpyxl: {e}")
    try:
        return pd.read_excel(path)
    except Exception as e:
        errors.append(f"default: {e}")
    raise RuntimeError("Could not read Excel: " + "; ".join(errors))


def load_table(path: str) -> pd.DataFrame:
    """Load file as CSV or Excel by extension."""
    path_lower = path.lower()
    if path_lower.endswith((".xlsx", ".xls")):
        return read_excel(path)
    return read_csv(path)
