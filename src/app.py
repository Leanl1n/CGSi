"""Streamlit app: CSV/Excel merger by country keywords and Brand JSON manager."""

import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from .brand_editor import (
        filter_brands_by_letter,
        load_brand_json,
        normalize_display_text,
        save_brand_json,
    )
except ImportError:
    from brand_editor import (
        filter_brands_by_letter,
        load_brand_json,
        normalize_display_text,
        save_brand_json,
    )
_merger_import_error = None
try:
    try:
        from .quarterly_csv_merger import (
            add_brand_from_keywords,
            add_date_columns,
            add_market_column,
            add_media_platform_column,
            add_media_type_column,
            drop_blank_url_rows,
            process_file,
            select_output_columns,
            set_engagement_from_sum,
        )
    except ImportError:
        from quarterly_csv_merger import (
            add_brand_from_keywords,
            add_date_columns,
            add_market_column,
            add_media_platform_column,
            add_media_type_column,
            drop_blank_url_rows,
            process_file,
            select_output_columns,
            set_engagement_from_sum,
        )
except Exception as e:
    _merger_import_error = e

_encoding_merger_import_error = None
try:
    try:
        from .annual_csv_merger import (
            CANONICAL_OUTPUT_COLUMNS,
            file_has_all_canonical_headers,
            headers_align,
            merge_if_aligned,
        )
    except ImportError:
        from annual_csv_merger import (
            CANONICAL_OUTPUT_COLUMNS,
            file_has_all_canonical_headers,
            headers_align,
            merge_if_aligned,
        )
except Exception as e:
    _encoding_merger_import_error = e


def get_base_dir() -> str:
    """Return project root directory."""
    return str(Path(__file__).resolve().parent.parent)


def _show_brand_action_popup() -> None:
    """Show success modal and optional follow-up action prompt."""
    if "brand_editor_show_popup" not in st.session_state or not st.session_state.brand_editor_show_popup:
        return
    msg = st.session_state.get("brand_editor_popup_message", "")
    action_type = st.session_state.get("brand_editor_popup_action", "add")
    if not msg:
        return
    if action_type == "remove":
        title, question, yes_label = "Removed successfully", "Do you want to remove more?", "Yes, remove more"
    else:
        title, question, yes_label = "Added successfully", "Do you want to add more?", "Yes, add more"

    @st.dialog(title)
    def _dialog():
        st.success(msg)
        st.write(question)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(yes_label, use_container_width=True, key="popup_yes"):
                st.session_state.brand_editor_show_popup = False
                st.session_state.brand_editor_popup_message = ""
                st.session_state.brand_editor_popup_action = ""
                st.rerun()
        with col2:
            if st.button("No, done", use_container_width=True, key="popup_no"):
                st.session_state.brand_editor_show_popup = False
                st.session_state.brand_editor_popup_message = ""
                st.session_state.brand_editor_popup_action = ""
                st.rerun()
    _dialog()


def _render_brand_json_manager() -> None:
    """Render Brand JSON manager UI (add/remove brands and keywords)."""
    _show_brand_action_popup()

    st.title("Brand JSON Manager")
    st.markdown("Edit **Brands** and **Keywords** in the brand configuration. Changes are saved immediately.")

    base_dir = get_base_dir()
    data = load_brand_json(base_dir)
    keys = sorted(data.keys()) if data else []

    action = st.radio(
        "What do you want to do?",
        [
            "Show all Brands and Keywords",
            "Add Keywords to a Brand",
            "Add a new Brand",
            "Remove a Brand",
            "Remove Keyword(s) from a Brand",
        ],
        horizontal=False,
    )

    if action == "Show all Brands and Keywords":
        st.subheader("All Brands and Keywords")
        if not data:
            st.info("No Brands yet. Add a Brand to get started.")
        else:
            total_keywords = sum(len(v) for v in data.values() if isinstance(v, list))
            letters = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
            selected_letter = st.selectbox("Choose letter", letters, key="brand_list_letter", index=0)
            filtered_keys = filter_brands_by_letter(keys, selected_letter, normalize_fn=normalize_display_text)
            filtered_kw_count = sum(
                len(data.get(b, [])) for b in filtered_keys if isinstance(data.get(b), list)
            )
            st.markdown(
                f"<p style='text-align: right; color: var(--text-muted); margin-top: -0.5rem;'>"
                f"{len(filtered_keys)} Brand(s) · {filtered_kw_count} Keyword(s)</p>",
                unsafe_allow_html=True,
            )
            if not filtered_keys:
                st.info(f"No Brands starting with **{selected_letter}**.")
            else:
                for brand in filtered_keys:
                    keywords = data.get(brand, [])
                    if not isinstance(keywords, list):
                        keywords = [str(keywords)]
                    brand_display = normalize_display_text(brand)
                    label = f"**{brand_display}** — {len(keywords)} Keyword(s)"
                    with st.expander(label, expanded=False):
                        if keywords:
                            for kw in keywords:
                                st.text(normalize_display_text(kw))
                        else:
                            st.caption("(no keywords)")

    elif action == "Add Keywords to a Brand":
        st.subheader("Add Keywords to a Brand")
        add_to_existing = st.radio(
            "Choose target",
            ["Append to an existing Brand", "Create a new Brand and add Keywords"],
            key="add_target",
        )
        if add_to_existing == "Append to an existing Brand":
            if not keys:
                st.info("No Brands yet. Use **Add a new Brand** first, or choose **Create a new Brand** below.")
            else:
                chosen = st.selectbox("Select Brand", keys, key="add_sel_key")
                new_values_raw = st.text_area(
                    "New Keywords (one per line)",
                    height=120,
                    placeholder="keyword1\nkeyword2\nkeyword3",
                    key="add_values_existing",
                )
                if st.button("Append to Brand"):
                    if not chosen:
                        st.warning("Select a Brand.")
                    else:
                        new_values = [v.strip() for v in new_values_raw.strip().splitlines() if v.strip()]
                        if not new_values:
                            st.warning("Enter at least one Keyword.")
                        else:
                            data[chosen] = data.get(chosen, []) + new_values
                            save_brand_json(data, base_dir)
                            st.session_state.brand_editor_show_popup = True
                            st.session_state.brand_editor_popup_message = f"Appended {len(new_values)} Keyword(s) to **{chosen}**."
                            st.session_state.brand_editor_popup_action = "add"
                            st.rerun()
        else:
            new_key = st.text_input("New Brand name", key="add_new_key_name")
            new_values_raw = st.text_area(
                "Keywords (one per line)",
                height=120,
                placeholder="keyword1\nkeyword2",
                key="add_values_new_key",
            )
            if st.button("Create Brand and add Keywords"):
                key_stripped = new_key.strip()
                if not key_stripped:
                    st.warning("Enter a Brand name.")
                else:
                    new_values = [v.strip() for v in new_values_raw.strip().splitlines() if v.strip()]
                    if key_stripped in data:
                        data[key_stripped] = data[key_stripped] + new_values
                        save_brand_json(data, base_dir)
                        st.session_state.brand_editor_show_popup = True
                        st.session_state.brand_editor_popup_message = f"Appended {len(new_values)} Keyword(s) to existing Brand **{key_stripped}**."
                        st.session_state.brand_editor_popup_action = "add"
                    else:
                        data[key_stripped] = new_values if new_values else []
                        save_brand_json(data, base_dir)
                        st.session_state.brand_editor_show_popup = True
                        st.session_state.brand_editor_popup_message = f"Created Brand **{key_stripped}** with {len(new_values)} Keyword(s)."
                        st.session_state.brand_editor_popup_action = "add"
                    st.rerun()

    elif action == "Add a new Brand":
        st.subheader("Add a new Brand")
        new_key = st.text_input("Brand name", key="new_key_name")
        new_values_raw = st.text_area(
            "Initial Keywords (one per line, optional)",
            height=100,
            key="new_key_values",
        )
        if st.button("Add Brand"):
            key_stripped = new_key.strip()
            if not key_stripped:
                st.warning("Enter a Brand name.")
            elif key_stripped in data:
                st.warning(f"Brand **{key_stripped}** already exists. Use **Add Keywords to a Brand** to append.")
            else:
                values = [v.strip() for v in new_values_raw.strip().splitlines() if v.strip()]
                data[key_stripped] = values
                save_brand_json(data, base_dir)
                st.session_state.brand_editor_show_popup = True
                st.session_state.brand_editor_popup_message = f"Added Brand **{key_stripped}** with {len(values)} Keyword(s)."
                st.session_state.brand_editor_popup_action = "add"
                st.rerun()

    elif action == "Remove a Brand":
        st.subheader("Remove a Brand")
        if not keys:
            st.info("No Brands to remove.")
        else:
            to_remove = st.selectbox("Select Brand to remove", keys, key="remove_key_sel")
            if st.button("Remove Brand"):
                if to_remove in data:
                    del data[to_remove]
                    save_brand_json(data, base_dir)
                    st.session_state.brand_editor_show_popup = True
                    st.session_state.brand_editor_popup_message = f"Removed Brand **{to_remove}**."
                    st.session_state.brand_editor_popup_action = "remove"
                    st.rerun()

    elif action == "Remove Keyword(s) from a Brand":
        st.subheader("Remove Keyword(s) from a Brand")
        if not keys:
            st.info("No Brands yet.")
        else:
            chosen = st.selectbox("Select Brand", keys, key="remove_val_key")
            values_in_key = data.get(chosen, [])
            if not values_in_key:
                st.info(f"Brand **{chosen}** has no Keywords.")
            else:
                to_remove = st.multiselect(
                    "Select Keyword(s) to remove",
                    values_in_key,
                    key="remove_val_sel",
                )
                if st.button("Remove selected Keywords"):
                    if not to_remove:
                        st.warning("Select at least one Keyword.")
                    else:
                        data[chosen] = [v for v in values_in_key if v not in to_remove]
                        save_brand_json(data, base_dir)
                        st.session_state.brand_editor_show_popup = True
                        st.session_state.brand_editor_popup_message = f"Removed {len(to_remove)} Keyword(s) from **{chosen}**."
                        st.session_state.brand_editor_popup_action = "remove"
                        st.rerun()


def _render_annual_csv_merge() -> None:
    """Render Annual CSV Merger: detect encoding, check header alignment, combine CSV/Excel (direct, no quarterly logic)."""
    st.title("Annual CSV Merger")
    with st.container():
        st.markdown(
            "Upload CSV or Excel files. Encoding is detected automatically (UTF-8, UTF-16, etc.). "
            "Each file is checked for columns matching the output schema (case-insensitive). "
            "Files are combined into a single CSV with columns in a fixed order."
        )

    if _encoding_merger_import_error is not None:
        st.error(f"Failed to load Annual CSV Merger module: {_encoding_merger_import_error}")
        return

    uploaded = st.file_uploader(
        "Upload CSV or Excel files",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        key="annual_csv_uploader",
    )

    paths: list[str] = []
    temp_dir = tempfile.mkdtemp()
    try:
        for f in uploaded:
            path = os.path.join(temp_dir, f.name)
            with open(path, "wb") as out:
                out.write(f.getvalue())
            paths.append(path)

        aligned, all_headers, _ = headers_align(paths)

        if not aligned and paths and all_headers:
            for path, h in zip(paths, all_headers):
                if h is None:
                    st.warning(f"Could not read headers from: **{os.path.basename(path)}**")
                    break
                if not file_has_all_canonical_headers(h):
                    st.warning("Headers do not match canonical output columns.")
                    break

        if aligned:
            st.success("Good to go — each file has matching columns (case-insensitive). You can combine the files.")
            if "encoding_merged_df" not in st.session_state and st.button("Combine files", key="encoding_merge_btn"):
                progress_bar = st.progress(0.0, text="Starting...")
                def on_progress(ratio: float, msg: str) -> None:
                    progress_bar.progress(min(1.0, ratio), text=msg)
                merged, report, _ = merge_if_aligned(paths, progress_callback=on_progress)
                progress_bar.progress(1.0, text="Done.")
                if merged is not None and not merged.empty:
                    st.session_state["encoding_merged_df"] = merged
                    st.session_state["encoding_merged_report"] = report
                    st.rerun()

        if "encoding_merged_df" in st.session_state and st.session_state.encoding_merged_df is not None:
            df = st.session_state.encoding_merged_df
            st.subheader("Merged Result")
            st.dataframe(df.head(100), use_container_width=True)
            st.subheader("Summary")
            st.metric("Total Rows", f"{len(df):,}")
            st.download_button(
                label="Download merged CSV",
                data=df.to_csv(index=False, encoding="utf-8-sig"),
                file_name="merged_annual.csv",
                mime="text/csv",
                key="encoding_download_btn",
            )
    finally:
        try:
            for p in paths:
                if os.path.isfile(p):
                    os.remove(p)
            if os.path.isdir(temp_dir):
                os.rmdir(temp_dir)
        except Exception:
            pass


def main() -> None:
    try:
        st.set_page_config(
            page_title="CGSi Tools",
            layout="centered",
        )
    except st.StreamlitAPIException:
        pass

    page = st.sidebar.selectbox(
        "Page",
        ["Quarterly CSV Merger", "Annual CSV Merger", "Brand Keywords Manager"],
        label_visibility="collapsed",
    )
    if page == "Brand Keywords Manager":
        _render_brand_json_manager()
        return

    if page == "Annual CSV Merger":
        _render_annual_csv_merge()
        return

    st.title("Quarterly CSV Merger")
    with st.container():
        st.markdown(
            "Merge CSV or Excel files by country keywords (ID, SG, TH, MY). "
            "Upload your files below, then preview and download the merged result."
        )

    if _merger_import_error is not None:
        st.error(f"Failed to load Quarterly CSV Merger module: {_merger_import_error}")
        st.info("Check that dependencies are installed (e.g. `pip install pandas openpyxl streamlit`) and restart the app.")
        return

    base_dir = get_base_dir()
    df = None

    uploaded = st.file_uploader(
        "Upload CSV or Excel files",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
    )
    if uploaded and st.button("Merge files"):
        temp_dir = tempfile.mkdtemp()
        paths: list[str] = []
        try:
            for f in uploaded:
                path = os.path.join(temp_dir, f.name)
                with open(path, "wb") as out:
                    out.write(f.getvalue())
                paths.append(path)

            n_steps = 1 + len(paths) + 1 + 6 + 1
            progress_bar = st.progress(0, text="Starting...")
            step = 0

            def advance(msg: str) -> None:
                nonlocal step
                step += 1
                progress_bar.progress(step / n_steps, text=msg)

            try:
                advance("Processing files...")
                frames = []
                for i, path in enumerate(paths):
                    progress_bar.progress((1 + i) / n_steps, text=f"Reading {os.path.basename(path)}...")
                    try:
                        frame = process_file(path, base_dir=base_dir)
                        if not frame.empty:
                            frames.append(frame)
                    except Exception as e:
                        st.warning(f"Skipped {os.path.basename(path)}: {e}")
                step = 1 + len(paths)

                if frames:
                    advance("Combining rows...")
                    try:
                        df = pd.concat(frames, ignore_index=True)
                    except Exception as e:
                        st.error(f"Failed to combine rows: {e}")
                        df = None
                    if df is not None and not df.empty:
                        def _safe_step(name: str, fn, *args, **kwargs):
                            nonlocal df
                            try:
                                df = fn(df, *args, **kwargs)
                                return True
                            except Exception as e:
                                st.warning(f"Step «{name}» skipped: {e}")
                                return False
                        advance("Removing blank URLs...")
                        _safe_step("Remove blank URLs", drop_blank_url_rows)
                        advance("Adding Market...")
                        _safe_step("Market", add_market_column)
                        advance("Adding Media Platform...")
                        _safe_step("Media Platform", add_media_platform_column)
                        advance("Adding Media Type...")
                        _safe_step("Media Type", add_media_type_column)
                        advance("Adding date columns...")
                        _safe_step("Date columns", add_date_columns)
                        advance("Calculating Engagement...")
                        _safe_step("Engagement", set_engagement_from_sum)
                        advance("Resolving Brand...")
                        _safe_step("Brand", add_brand_from_keywords, base_dir=base_dir)
                    progress_bar.progress(1.0, text="Done.")
                    if df is not None and not df.empty:
                        st.success(f"Merged **{len(df)}** rows from {len(uploaded)} file(s).")
                    else:
                        st.warning("Merge completed but no rows remained after pipeline steps.")
                else:
                    progress_bar.progress(1.0, text="Done.")
                    st.warning("No rows matched country keywords (ID/SG/TH/MY in filename or name column).")
                    df = None
            except Exception as e:
                progress_bar.progress(1.0, text="Error.")
                st.error(f"Merge failed: {e}")
                df = None
        except Exception as e:
            st.error(f"Failed to prepare files: {e}")
        finally:
            try:
                for p in paths:
                    if os.path.isfile(p):
                        os.remove(p)
                if os.path.isdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception:
                pass

    if df is not None and not df.empty:
        try:
            out_df = select_output_columns(df)
            st.subheader("Merged Result")
            st.dataframe(out_df.head(100), use_container_width=True)

            st.subheader("Summary")
            n_rows = len(out_df)
            n_cols = len(out_df.columns)
            n_countries = df["Country"].nunique() if "Country" in df.columns else 0
            n_files = len(uploaded) if uploaded else 0

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{n_rows:,}")
            with col2:
                st.metric("Total Columns", f"{n_cols}")
            with col3:
                st.metric("Countries", n_countries)
            with col4:
                st.metric("Files Merged", n_files)

            if "Country" in df.columns and n_countries > 0:
                st.caption("Rows per country")
                counts = df["Country"].value_counts().sort_index()
                cols = st.columns(min(len(counts), 4))
                for i, (country, count) in enumerate(counts.items()):
                    with cols[i % len(cols)]:
                        st.metric(country, f"{count:,}")

            st.download_button(
                label="Download merged CSV",
                data=out_df.to_csv(index=False, encoding="utf-8-sig"),
                file_name="merged_data.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Preview or download failed: {e}")
            st.dataframe(df.head(100), use_container_width=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        st.error(f"App error: {e}")
        st.code(traceback.format_exc())
