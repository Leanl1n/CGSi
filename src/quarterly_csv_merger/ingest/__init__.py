"""Ingest: load files and assign country from filename or name column."""

from .country_keywords import process_file, collect_files

__all__ = ["process_file", "collect_files"]
