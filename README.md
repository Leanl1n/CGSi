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

**Can you update the JSON file when deployed?**  
Yes and no:

- **During a session**: The Brand JSON Manager can read and write `data/brand.json` as usual. Edits are saved to the app’s filesystem and stay in effect until the app restarts or goes to sleep.
- **After restart / redeploy**: On Streamlit Community Cloud (and similar hosts), the filesystem is **ephemeral**. The container is recreated from your repo, so any changes to `data/brand.json` are **lost**. Only the version in your Git repo is kept.

So **updates are possible during a run, but they do not persist** across restarts unless you add persistent storage.

**If you need persistent brand data when deployed:**

1. **Keep using the file locally** – Deploy with the `data/brand.json` you want as the default. Users can still edit during a session; just know changes won’t survive restarts.
2. **Use external storage** – Store brand config in a database (e.g. SQLite in a persistent volume, Supabase, etc.) or object storage (e.g. S3, GCS). Then change `brand_editor/editor.py` to read/write from that store when running in the cloud (e.g. via an env var or Streamlit secrets).
3. **Manage brand.json in Git** – Treat `data/brand.json` as the source of truth: edit it in the repo and redeploy when you want to update brands. The in-app Brand JSON Manager then only affects the current session.
