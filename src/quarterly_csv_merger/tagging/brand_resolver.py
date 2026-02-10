"""Resolve Brand column from Keywords and brand JSON alias map."""

import json
from pathlib import Path
import pandas as pd

from .._deps import BRAND_JSON_FILENAME
from ..columns import build_keywords_dict


def load_brand_alias_map(brand_json_path: str | Path) -> dict[str, str]:
    """Load brand JSON and build lowercase alias -> display name map; return {} if missing/invalid."""
    path = Path(brand_json_path)
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    alias_to_brand: dict[str, str] = {}
    for brand_name, aliases in data.items():
        brand = str(brand_name).strip()
        if brand:
            alias_to_brand[brand.lower()] = brand
        if isinstance(aliases, list):
            for a in aliases:
                if isinstance(a, str) and a.strip():
                    alias_to_brand[a.strip().lower()] = brand
    return alias_to_brand


def resolve_brand_from_keywords(keywords_list: list[str], alias_to_brand: dict[str, str]) -> str:
    """Match keywords last-first against alias map; return first match or 'Unknown'."""
    for kw in reversed(keywords_list):
        k = kw.strip()
        if k and k.lower() in alias_to_brand:
            return alias_to_brand[k.lower()]
    return "Unknown"


def add_brand_from_keywords(df: pd.DataFrame, base_dir: str | None = None) -> pd.DataFrame:
    """Resolve Brand column from Keywords and brand JSON."""
    if base_dir is None:
        base_dir = str(Path(__file__).resolve().parent.parent.parent.parent)
    keywords_by_row, _ = build_keywords_dict(df)
    if not keywords_by_row:
        df = df.copy()
        if "Brand" not in df.columns:
            df["Brand"] = "Unknown"
        return df
    brand_path = Path(base_dir) / BRAND_JSON_FILENAME
    alias_to_brand = load_brand_alias_map(brand_path)
    if not alias_to_brand:
        df = df.copy()
        if "Brand" not in df.columns:
            df["Brand"] = "Unknown"
        return df
    brands = [
        resolve_brand_from_keywords(keywords_by_row.get(i, []), alias_to_brand)
        for i in df.index
    ]
    df = df.copy()
    df["Brand"] = brands
    return df
