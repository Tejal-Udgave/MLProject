from collections import Counter
from hashlib import sha256
from html import escape
from io import BytesIO
from pathlib import Path
import tempfile
import time

import pandas as pd
import streamlit as st

from apriori import apriori, generate_rules, itemsets_dataframe, load_transactions
from sentinel_ui import (
    distribution_figure,
    inject_theme_css,
    itemset_size_figure,
    support_confidence_figure,
    top_rules_figure,
)


CHUNK_SIZE = 100_000
ITEMSET_COLUMNS = ["Itemset", "Itemset size", "Support"]
RULE_COLUMNS = ["Antecedents", "Consequents", "Support", "Confidence", "Lift"]
SHIELD_ICON = """
<svg viewBox="0 0 32 32" width="25" height="25" aria-hidden="true">
  <path d="M16 3 27 7v8c0 7.2-4.4 11.7-11 14-6.6-2.3-11-6.8-11-14V7z"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="m10.5 15.5 3.5 3.5 7.5-8" fill="none" stroke="currentColor"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


st.set_page_config(
    page_title="SENTINEL | Network Traffic Intelligence",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "sentinel_theme" not in st.session_state:
    st.session_state["sentinel_theme"] = "Dark"
if st.session_state.get("sentinel_state_version") != 2:
    st.session_state.pop("analysis_result", None)
    st.session_state["sentinel_state_version"] = 2

theme = st.session_state["sentinel_theme"]
inject_theme_css(theme)


@st.cache_data(show_spinner=False, max_entries=2)
def inspect_csv(csv_bytes):
    header = pd.read_csv(BytesIO(csv_bytes), nrows=0)
    columns = list(header.columns)
    label_column = "Label" if "Label" in columns else None
    feature_columns = [column for column in columns if column != label_column]
    if not feature_columns:
        raise ValueError("The CSV must contain at least one feature column.")

    protocol_column = next(
        (
            column
            for column in columns
            if column.casefold() in {"protocol", "protocol_name"}
        ),
        None,
    )
    insight_columns = list(
        dict.fromkeys(
            column
            for column in (feature_columns[0], label_column, protocol_column)
            if column is not None
        )
    )
    distributions = {column: Counter() for column in (label_column, protocol_column) if column}
    categories = []
    row_count = 0

    for chunk in pd.read_csv(
        BytesIO(csv_bytes),
        usecols=insight_columns,
        chunksize=CHUNK_SIZE,
    ):
        row_count += len(chunk)
        for column in distributions:
            counts = chunk[column].dropna().astype(str).value_counts()
            distributions[column].update(counts.to_dict())
            if column == label_column:
                categories.extend(
                    value for value in counts.index if value not in categories
                )

    return {
        "columns": columns,
        "feature_count": len(feature_columns),
        "row_count": row_count,
        "label_column": label_column,
        "protocol_column": protocol_column,
        "categories": categories,
        "distributions": {
            column: dict(counts) for column, counts in distributions.items()
        },
    }


def write_category_csv(csv_bytes, category, label_column, output_path):
    wrote_header = False
    for chunk in pd.read_csv(BytesIO(csv_bytes), chunksize=CHUNK_SIZE):
        if label_column not in chunk.columns:
            raise ValueError(f"The dataset does not contain the expected {label_column} column.")
        matching = chunk.loc[chunk[label_column].astype("string") == category]
        if matching.empty:
            continue
        matching.to_csv(
            output_path,
            mode="a" if wrote_header else "w",
            header=not wrote_header,
            index=False,
        )
        wrote_header = True

    if not wrote_header:
        raise ValueError(f"No records matched the selected category “{category}”.")


def display_distribution(distribution, theme, key):
    if not distribution:
        render_empty_visual("The dataset contains no non-empty values for this field.")
        return
    st.plotly_chart(
        distribution_figure(distribution, theme),
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
        key=key,
    )


def render_results_table(dataframe, key_prefix, search_columns, sort_options, default_sort):
    search_column, sort_column, size_column = st.columns([2, 1, 0.8])
    query = search_column.text_input("Search results", key=f"{key_prefix}_search")
    sort_by = sort_column.selectbox(
        "Sort by",
        sort_options,
        index=sort_options.index(default_sort),
        key=f"{key_prefix}_sort",
    )
    page_size = size_column.selectbox(
        "Rows",
        [10, 25, 50, 100],
        index=1,
        key=f"{key_prefix}_page_size",
    )

    filtered = dataframe
    if query:
        matching = pd.Series(False, index=filtered.index)
        for column in search_columns:
            matching |= filtered[column].astype(str).str.contains(
                query, case=False, regex=False
            )
        filtered = filtered.loc[matching]
    filtered = filtered.sort_values(
        sort_by,
        ascending=sort_by in {"Itemset", "Antecedents"},
    )

    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    page_key = f"{key_prefix}_page"
    if st.session_state.get(page_key, 1) > total_pages:
        st.session_state[page_key] = total_pages
    page_column, summary_column = st.columns([1, 4], vertical_alignment="center")
    if total_pages > 1:
        page_number = page_column.selectbox(
            "Page",
            options=list(range(1, total_pages + 1)),
            key=page_key,
        )
    else:
        page_number = 1
        page_column.caption("Page 1 of 1")
    start = (int(page_number) - 1) * page_size
    visible = filtered.iloc[start : start + page_size]
    end = min(start + len(visible), len(filtered))
    summary_column.caption(
        f"Showing {start + 1:,}–{end:,} of {len(filtered):,} matching rows"
        if len(filtered)
        else "No rows match this search."
    )

    headers = {
        "Itemset": "Itemset",
        "Itemset size": "Size",
        "Antecedents": "Antecedents",
        "Consequents": "Consequents",
        "Support": "Support",
        "Confidence": "Confidence",
        "Lift": "Lift",
    }
    text_columns = {"Itemset", "Antecedents", "Consequents"}
    number_formats = {
        "Itemset size": "{:.0f}",
        "Support": "{:.4f}",
        "Confidence": "{:.4f}",
        "Lift": "{:.3f}",
    }
    header_html = "".join(
        f"<th>{escape(headers.get(column, column))}</th>" for column in dataframe.columns
    )
    body_html = []
    for row in visible.itertuples(index=False, name=None):
        cells = []
        for column, value in zip(dataframe.columns, row):
            if column in text_columns:
                cell_class = "sentinel-text-cell"
                formatted = escape(str(value))
            elif column in number_formats:
                cell_class = "sentinel-number-cell"
                formatted = number_formats[column].format(float(value))
            else:
                cell_class = ""
                formatted = escape(str(value))
            cells.append(f'<td class="{cell_class}">{formatted}</td>')
        body_html.append(f"<tr>{''.join(cells)}</tr>")
    if not body_html:
        body_html.append(
            f'<tr><td colspan="{len(dataframe.columns)}">No matching results.</td></tr>'
        )

    st.markdown(
        '<div class="sentinel-table-wrap"><table class="sentinel-results-table">'
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{''.join(body_html)}</tbody></table></div>",
        unsafe_allow_html=True,
    )
    st.download_button(
        "Download CSV",
        dataframe.to_csv(index=False).encode("utf-8"),
        f"sentinel_{key_prefix}.csv",
        "text/csv",
        key=f"{key_prefix}_download",
    )


def render_empty_visual(message):
    st.markdown(
        f"""
        <div class="sentinel-empty">
          <div class="sentinel-empty-mark">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M12 3 20 7.2v5.1c0 4.2-3 7.1-8 8.7-5-1.6-8-4.5-8-8.7V7.2L12 3Z"
                stroke="currentColor" stroke-width="1.5"/>
              <path d="M8.5 12h7M12 8.5v7" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            Insight unavailable
          </div>
          <div>{escape(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        f"""
        <div class="sentinel-wordmark">
          <div class="sentinel-mark">{SHIELD_ICON}</div>
          <div>
            <div class="sentinel-name">SENTINEL</div>
            <div class="sentinel-tagline">Pattern discovery workspace</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sentinel-sidebar-group">Dataset</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload preprocessed CSV",
        type=["csv"],
        help="One network-traffic transaction per row. An optional Label column enables category filtering.",
    )
    csv_bytes = uploaded_file.getvalue() if uploaded_file else None
    dataset_fingerprint = sha256(csv_bytes).hexdigest() if csv_bytes is not None else None
    dataset_info = None
    dataset_error = None
    if csv_bytes is not None:
        try:
            dataset_info = inspect_csv(csv_bytes)
            st.markdown(
                f'<div class="sentinel-file">{escape(uploaded_file.name)}</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                f"Ready · {dataset_info['row_count']:,} CSV records · "
                f"{len(dataset_info['columns'])} columns"
            )
        except (
            pd.errors.ParserError,
            pd.errors.EmptyDataError,
            UnicodeDecodeError,
            ValueError,
        ) as exc:
            dataset_error = str(exc)
            st.error(f"Dataset validation failed: {dataset_error}")
    else:
        st.caption("No dataset selected")

    st.markdown(
        '<div class="sentinel-sidebar-group">Mining parameters</div>',
        unsafe_allow_html=True,
    )
    min_support = st.number_input(
        "Minimum support",
        min_value=0.000001,
        max_value=1.0,
        value=0.05,
        step=0.01,
        format="%.4f",
        help="Minimum proportion of transactions that must contain an itemset. The Apriori backend requires a value in (0, 1].",
    )
    min_confidence = st.number_input(
        "Minimum confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.60,
        step=0.01,
        format="%.2f",
        help="Minimum conditional probability for an association rule, between 0 and 1.",
    )
    min_lift = st.number_input(
        "Minimum lift",
        min_value=0.0,
        value=1.20,
        step=0.1,
        format="%.2f",
        help="Minimum observed-to-expected co-occurrence ratio. Higher lift indicates a stronger association.",
    )

    selected_category = None
    if dataset_info and dataset_info["label_column"] and dataset_info["categories"]:
        selected_category = st.selectbox(
            "Activity category",
            ["All categories", *dataset_info["categories"]],
            help="Filter the transactions by their existing Label values.",
        )
        if selected_category == "All categories":
            selected_category = None
    elif dataset_info:
        st.caption("Category filtering is unavailable: no Label column was found.")

    st.markdown('<div class="sentinel-sidebar-group">Analysis</div>', unsafe_allow_html=True)
    run_analysis = st.button(
        "Run Analysis",
        type="primary",
        width="stretch",
        disabled=dataset_info is None or dataset_error is not None,
    )


result = st.session_state.get("analysis_result")
result_matches_dataset = bool(
    result
    and dataset_fingerprint is not None
    and result["dataset_fingerprint"] == dataset_fingerprint
    and result["category"] == selected_category
)
result_matches_parameters = bool(
    result
    and result["parameters"]
    == {
        "support": min_support,
        "confidence": min_confidence,
        "lift": min_lift,
    }
)
result_matches_current = result_matches_dataset and result_matches_parameters

if result and result_matches_current:
    status_text = "Analysis complete"
    status_state = "success"
elif result:
    status_text = "Previous analysis"
    status_state = "warning"
elif dataset_info:
    status_text = "Dataset ready"
    status_state = "warning"
else:
    status_text = "Awaiting dataset"
    status_state = "idle"

header, theme_column = st.columns([5, 1.3], vertical_alignment="center")
with header:
    st.markdown(
        f"""
        <div class="sentinel-wordmark">
          <div class="sentinel-mark">{SHIELD_ICON}</div>
          <div>
            <div class="sentinel-name">SENTINEL</div>
            <div class="sentinel-tagline">Network traffic intelligence &amp; pattern discovery</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with theme_column:
    st.selectbox(
        "Theme",
        ["Dark", "Light"],
        key="sentinel_theme",
        label_visibility="collapsed",
    )

status_column, _ = st.columns([2, 5])
with status_column:
    st.markdown(
        f'<div class="sentinel-status" data-state="{status_state}">'
        f'<span class="sentinel-status-dot"></span>{status_text}</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="sentinel-intro">
      <strong>Discover recurring network-traffic patterns.</strong>
      Association rules summarize which observed items occur together, using support, confidence,
      and lift. SENTINEL analyzes uploaded datasets; it is not a live monitoring or intrusion-detection service.
    </div>
    """,
    unsafe_allow_html=True,
)

if result and not result_matches_current:
    if not result_matches_dataset:
        st.warning(
            "The results below belong to an earlier dataset or category selection. "
            "Run analysis to refresh them."
        )
    else:
        st.warning(
            "Thresholds have changed since this analysis. Run analysis to refresh the displayed results."
        )

if run_analysis and dataset_info is not None:
    started_at = time.perf_counter()
    analysis_succeeded = False
    try:
        with st.status("Running association analysis", expanded=True) as status:
            status.write("Preparing transactions using the existing project loader.")
            if selected_category is None:
                transactions = load_transactions(BytesIO(csv_bytes), include_label=False)
            else:
                with tempfile.TemporaryDirectory(prefix="sentinel-") as temp_dir:
                    filtered_path = Path(temp_dir) / "selected_category.csv"
                    write_category_csv(
                        csv_bytes,
                        selected_category,
                        dataset_info["label_column"],
                        filtered_path,
                    )
                    transactions = load_transactions(
                        str(filtered_path),
                        include_label=False,
                    )

            status.write("Mining frequent itemsets with the existing Apriori implementation.")
            frequent = apriori(transactions, min_support=min_support)
            status.write("Generating rules with the configured confidence and lift thresholds.")
            rules = generate_rules(
                frequent,
                min_confidence=min_confidence,
                min_lift=min_lift,
            )

            frequent_frame = itemsets_dataframe(frequent).rename(
                columns={"Length": "Itemset size"}
            )[ITEMSET_COLUMNS]
            rules_frame = pd.DataFrame(
                rules,
                columns=["Antecedent", "Consequent", "Support", "Confidence", "Lift"],
            ).rename(
                columns={"Antecedent": "Antecedents", "Consequent": "Consequents"}
            )[RULE_COLUMNS]
            status.update(label="Analysis complete", state="complete", expanded=False)

        st.session_state["analysis_result"] = {
            "records": len(transactions),
            "itemsets": frequent_frame,
            "rules": rules_frame,
            "execution_time": time.perf_counter() - started_at,
            "category": selected_category,
            "dataset_fingerprint": dataset_fingerprint,
            "dataset_info": dataset_info,
            "parameters": {
                "support": min_support,
                "confidence": min_confidence,
                "lift": min_lift,
            },
        }
        analysis_succeeded = True
    except (
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
        UnicodeDecodeError,
        ValueError,
    ) as exc:
        st.error(f"Analysis could not be completed: {exc}")
    except Exception as exc:
        st.error(f"Unexpected analysis failure: {exc}")
        st.exception(exc)

    if analysis_succeeded:
        st.rerun()

metric_columns = st.columns(4)
metric_values = (
    [
        f"{result['records']:,}",
        f"{len(result['itemsets']):,}",
        f"{len(result['rules']):,}",
        f"{result['execution_time']:.2f} s",
    ]
    if result and result_matches_current
    else ["—", "—", "—", "—"]
)
for column, label, value in zip(
    metric_columns,
    ["Records analysed", "Frequent itemsets", "Association rules", "Execution time"],
    metric_values,
):
    column.metric(label, value)

overview_tab, itemsets_tab, rules_tab, insights_tab = st.tabs(
    ["Overview", "Frequent Itemsets", "Association Rules", "Dataset Insights"]
)

with overview_tab:
    first_row_left, first_row_right = st.columns(2, gap="medium")
    with first_row_left, st.container(border=True):
        st.markdown('<span class="sentinel-chart-card-marker"></span>', unsafe_allow_html=True)
        st.markdown('<div class="sentinel-section-heading">Traffic composition</div>', unsafe_allow_html=True)
        source_info = result["dataset_info"] if result and result_matches_current else dataset_info
        if source_info and source_info["label_column"]:
            st.markdown(
                f'<div class="sentinel-chart-subtitle">Uploaded CSV · {escape(source_info["label_column"])} values.</div>',
                unsafe_allow_html=True,
            )
            display_distribution(
                source_info["distributions"].get(source_info["label_column"], {}),
                theme,
                key="overview_activity_distribution",
            )
        elif source_info and source_info["protocol_column"]:
            st.markdown(
                f'<div class="sentinel-chart-subtitle">Uploaded CSV · {escape(source_info["protocol_column"])} values.</div>',
                unsafe_allow_html=True,
            )
            display_distribution(
                source_info["distributions"].get(source_info["protocol_column"], {}),
                theme,
                key="overview_protocol_distribution",
            )
        else:
            st.markdown(
                '<div class="sentinel-chart-subtitle">A dataset Label or Protocol field is required.</div>',
                unsafe_allow_html=True,
            )
            render_empty_visual(
                "A Label or Protocol column is not available. Add an existing category field to the uploaded CSV to see this distribution."
            )

    with first_row_right, st.container(border=True):
        st.markdown('<span class="sentinel-chart-card-marker"></span>', unsafe_allow_html=True)
        st.markdown('<div class="sentinel-section-heading">Frequent itemset sizes</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sentinel-chart-subtitle">Count of discovered itemsets by number of items.</div>',
            unsafe_allow_html=True,
        )
        if result and result_matches_current and not result["itemsets"].empty:
            st.plotly_chart(
                itemset_size_figure(result["itemsets"], theme),
                width="stretch",
                config={"displayModeBar": False, "responsive": True},
                key="itemset_size_distribution",
            )
        else:
            render_empty_visual(
                "Complete an analysis with the current dataset and thresholds to populate itemset-size counts."
            )

    second_row_left, second_row_right = st.columns(2, gap="medium")
    with second_row_left, st.container(border=True):
        st.markdown('<span class="sentinel-chart-card-marker"></span>', unsafe_allow_html=True)
        st.markdown('<div class="sentinel-section-heading">Highest-lift rules</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sentinel-chart-subtitle">Top six returned rules ranked by lift.</div>',
            unsafe_allow_html=True,
        )
        if result and result_matches_current and not result["rules"].empty:
            st.plotly_chart(
                top_rules_figure(result["rules"], theme),
                width="stretch",
                config={"displayModeBar": False, "responsive": True},
                key="highest_lift_rules",
            )
        else:
            render_empty_visual(
                "No qualifying rules are available. Lower the confidence or lift threshold, or check the dataset."
            )

    with second_row_right, st.container(border=True):
        st.markdown('<span class="sentinel-chart-card-marker"></span>', unsafe_allow_html=True)
        st.markdown('<div class="sentinel-section-heading">Support vs. confidence</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sentinel-chart-subtitle">Returned rules; colour shows lift (top 1,000 by lift).</div>',
            unsafe_allow_html=True,
        )
        if result and result_matches_current and not result["rules"].empty:
            st.plotly_chart(
                support_confidence_figure(result["rules"], theme),
                width="stretch",
                config={"displayModeBar": False, "responsive": True},
                key="support_confidence_scatter",
            )
            if len(result["rules"]) == 1:
                st.caption(
                    "One qualifying rule was returned at the selected thresholds; its point is shown above."
                )
        else:
            render_empty_visual(
                "The plot appears when the backend returns at least one qualifying association rule."
            )

with itemsets_tab:
    if result and result_matches_current:
        if result["itemsets"].empty:
            st.info("No frequent itemsets met the selected minimum support.")
        else:
            render_results_table(
                result["itemsets"],
                "itemsets",
                ["Itemset"],
                ["Support", "Itemset size", "Itemset"],
                "Support",
            )
    else:
        st.caption("Run an analysis to inspect frequent itemsets.")

with rules_tab:
    if result and result_matches_current:
        if result["rules"].empty:
            st.info("No rules met the selected confidence and lift thresholds.")
        else:
            st.caption("Rule rankings and chart values are calculated from the backend's returned rules.")
            render_results_table(
                result["rules"],
                "rules",
                ["Antecedents", "Consequents"],
                ["Lift", "Confidence", "Support"],
                "Lift",
            )
    else:
        st.caption("Run an analysis to inspect association rules.")

with insights_tab:
    source_info = result["dataset_info"] if result and result_matches_current else dataset_info
    if source_info:
        if source_info["protocol_column"] and source_info["label_column"]:
            with st.container(border=True):
                st.markdown('<span class="sentinel-chart-card-marker"></span>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="sentinel-section-heading">Protocol distribution</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="sentinel-chart-subtitle">Observed values in {escape(source_info["protocol_column"])}.</div>',
                    unsafe_allow_html=True,
                )
                display_distribution(
                    source_info["distributions"].get(source_info["protocol_column"], {}),
                    theme,
                    key="dataset_protocol_distribution",
                )
        elif source_info["protocol_column"] is None and source_info["label_column"] is None:
            st.info("This dataset has no Label or Protocol field to summarize.")
        else:
            st.caption("The available traffic-composition chart is shown in Overview.")

        if result and result_matches_current:
            st.caption(
                f"Analysed {result['records']:,} transactions from "
                f"{source_info['row_count']:,} CSV records"
                + (
                    f" filtered to category “{result['category']}”."
                    if result["category"]
                    else "."
                )
            )
            if result["records"] < source_info["row_count"] and not result["category"]:
                st.caption(
                    "The transaction loader drops rows containing missing values; "
                    "the analysed transaction count reflects the rows it returned."
                )
        else:
            st.caption(
                f"Uploaded dataset: {source_info['row_count']:,} CSV records · "
                f"{len(source_info['columns'])} columns."
            )
    else:
        st.markdown(
            f"""
            <div class="sentinel-empty">
              <div class="sentinel-overline">Dataset insights</div>
              <div>Upload a preprocessed CSV to inspect its available activity categories and protocol values.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
