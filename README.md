# CGSi CSV Merger

Merge CSV/Excel files by country (Indonesia, Singapore, Thailand, Malaysia). Reads from CSV or Excel, filters by keyword in the name column, applies cleaning and tagging (market, media platform, brand), and outputs combined data. Includes a Streamlit app for drag-and-drop merge and a Brand JSON Manager.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Streamlit app (recommended)

From the project root:

```bash
python main.py
```

Or directly:

```bash
streamlit run src/app.py
```

### CLI merger

Merge from a folder or file and save to `output/data.csv`:

```bash
python -m src.quarterly_csv_merger [path]
```

Default path is the configured raw data folder. Use `--help` for options.

## Project layout

```
├── main.py                 # Streamlit entry point
├── data/
│   └── brand.json          # Brand configuration (editable via Brand JSON Manager)
├── raw_data/               # Input data (gitignored)
├── output/                 # Merged CSV output (gitignored)
├── requirements.txt
└── src/
    ├── __init__.py
    ├── app.py              # Streamlit UI (drag-and-drop, preview, download)
    ├── annual_csv_merger/  # Annual merge: header alignment, canonical columns
    │   ├── __init__.py
    │   ├── encoding.py
    │   ├── header_check.py
    │   └── merge.py
    ├── brand_editor/       # Brand JSON: load, save, normalize (UI in app)
    │   ├── __init__.py
    │   └── editor.py
    ├── constants/          # Config: keywords, column names, paths
    │   └── __init__.py
    ├── reader/             # CSV/Excel loading, encoding detection
    │   └── __init__.py
    └── quarterly_csv_merger/      # Merge pipeline (structured by role)
        ├── __init__.py            # Public API
        ├── __main__.py            # CLI: python -m src.quarterly_csv_merger
        ├── _deps.py               # Constants/reader import fallback
        ├── pipeline.py            # Orchestrates: ingest → cleaning → tagging → transforms → output
        ├── ingest/                # Load files, assign country from filename/name
        │   └── country_keywords.py
        ├── cleaning/              # Remove invalid rows
        │   └── blank_url_remover.py
        ├── tagging/               # Tagging logic (Market, Media Platform, Brand)
        │   ├── market_tagger.py
        │   ├── media_platform_tagger.py
        │   └── brand_resolver.py
        ├── transforms/            # Add/derive columns
        │   ├── date_columns.py
        │   └── engagement_sum.py
        └── columns/               # Column discovery and output selection
            └── column_finder.py
```

- **constants** – Country keywords (ID, SG, TH, MY), column names, output columns, paths.
- **reader** – `read_csv`, `read_excel`, `load_table`, encoding detection.
- **brand_editor** – Load/save `data/brand.json`, normalize display text, filter brands by letter; Brand JSON Manager UI in app.
- **annual_csv_merger** – Header alignment and canonical column checks for annual merge flows (used by app when merging multiple files).
- **quarterly_csv_merger** – **ingest** (load + country), **cleaning** (blank URL), **tagging** (market, media, brand), **transforms** (dates, engagement), **columns** (discovery + output), **pipeline** (orchestration).
- **app** – Streamlit: drag-and-drop upload, merge, preview, download CSV; Brand JSON Manager.
