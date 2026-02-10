"""Brand JSON data layer: load, save, normalize."""

import json
import re
from pathlib import Path

try:
    from ..constants import BRAND_JSON_FILENAME
except ImportError:
    from constants import BRAND_JSON_FILENAME


def _get_base_dir() -> str:
    """Return project root directory."""
    return str(Path(__file__).resolve().parent.parent.parent)


def get_brand_json_path(base_dir: str | None = None) -> Path:
    """Return path to brand JSON file."""
    root = base_dir if base_dir is not None else _get_base_dir()
    return Path(root) / BRAND_JSON_FILENAME


def load_brand_json(base_dir: str | None = None) -> dict:
    """Load brand JSON; return empty dict if missing or invalid."""
    path = get_brand_json_path(base_dir)
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_brand_json(data: dict, base_dir: str | None = None) -> None:
    """Save brand data to JSON file."""
    path = get_brand_json_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_display_text(raw: str) -> str:
    """Normalize text for display: strip and collapse whitespace."""
    if not raw or not isinstance(raw, str):
        return ""
    s = raw.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def filter_brands_by_letter(brand_keys: list[str], letter: str, normalize_fn=None) -> list[str]:
    """Return brand keys whose normalized name starts with the given letter."""
    norm = normalize_fn or normalize_display_text
    return [b for b in brand_keys if norm(b).upper().startswith(letter)]
