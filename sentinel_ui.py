import pandas as pd
import plotly.graph_objects as go
import streamlit as st


THEMES = {
    "Dark": {
        "page": "#0b1420",
        "sidebar": "#0e1a28",
        "panel": "#111f2e",
        "panel_alt": "#172737",
        "elevated": "#192a3b",
        "text": "#e7eef5",
        "muted": "#9babb9",
        "subtle": "#718495",
        "border": "#253849",
        "accent": "#50c4c0",
        "accent_strong": "#2aa7a4",
        "blue": "#76a9e8",
        "success": "#50c4a0",
        "warning": "#e3b765",
        "error": "#e17979",
        "chart_grid": "#263849",
        "chart_axis": "#8193a3",
        "chart_hover": "#1b2b3b",
        "input": "#132334",
        "button_text": "#0b1420",
        "table_head": "#192b3c",
        "table_row": "#111f2e",
        "table_alt": "#142435",
        "chart_palette": ["#50c4c0", "#76a9e8", "#d5aa67", "#9a8de0", "#70b990"],
        "shadow": "0 4px 16px rgba(0, 0, 0, .12)",
    },
    "Light": {
        "page": "#f3f6f8",
        "sidebar": "#eaf0f4",
        "panel": "#ffffff",
        "panel_alt": "#f6f9fb",
        "elevated": "#edf3f6",
        "text": "#172b3b",
        "muted": "#526a7a",
        "subtle": "#718695",
        "border": "#d5e0e7",
        "accent": "#087f7d",
        "accent_strong": "#096b6b",
        "blue": "#2865a5",
        "success": "#16845f",
        "warning": "#9c6812",
        "error": "#ad3d3d",
        "chart_grid": "#e2e9ee",
        "chart_axis": "#526a7a",
        "chart_hover": "#ffffff",
        "input": "#ffffff",
        "button_text": "#ffffff",
        "table_head": "#eaf1f4",
        "table_row": "#ffffff",
        "table_alt": "#f5f8fa",
        "chart_palette": ["#087f7d", "#2865a5", "#a46a16", "#715bb3", "#36805e"],
        "shadow": "0 3px 12px rgba(30, 52, 70, .05)",
    },
}


def inject_theme_css(theme):
    colors = THEMES[theme]
    st_css = f"""
    <style>
    :root {{
      color-scheme: {"light" if theme == "Light" else "dark"};
      --sentinel-page: {colors["page"]};
      --sentinel-sidebar: {colors["sidebar"]};
      --sentinel-panel: {colors["panel"]};
      --sentinel-panel-alt: {colors["panel_alt"]};
      --sentinel-elevated: {colors["elevated"]};
      --sentinel-text: {colors["text"]};
      --sentinel-muted: {colors["muted"]};
      --sentinel-subtle: {colors["subtle"]};
      --sentinel-border: {colors["border"]};
      --sentinel-accent: {colors["accent"]};
      --sentinel-accent-strong: {colors["accent_strong"]};
      --sentinel-blue: {colors["blue"]};
      --sentinel-success: {colors["success"]};
      --sentinel-warning: {colors["warning"]};
      --sentinel-error: {colors["error"]};
      --sentinel-input: {colors["input"]};
      --sentinel-button-text: {colors["button_text"]};
      --sentinel-table-head: {colors["table_head"]};
      --sentinel-table-row: {colors["table_row"]};
      --sentinel-table-alt: {colors["table_alt"]};
      --sentinel-shadow: {colors["shadow"]};
    }}
    .stApp {{ background: var(--sentinel-page) !important; color: var(--sentinel-text); }}
    [data-testid="stAppViewContainer"] {{ background: var(--sentinel-page) !important; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] {{
      background: var(--sentinel-sidebar) !important;
      border-right: 1px solid var(--sentinel-border);
    }}
    [data-testid="stSidebar"] > div {{ padding-top: .8rem; }}
    .block-container {{ max-width: 1580px; padding: 3rem 1.65rem 2rem; }}
    h1, h2, h3, h4 {{ color: var(--sentinel-text) !important; letter-spacing: -.02em; }}
    p, [data-testid="stCaptionContainer"] {{ color: var(--sentinel-muted); }}
    [data-testid="stCaptionContainer"] p {{ color: var(--sentinel-muted) !important; }}
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {{ color: var(--sentinel-text) !important; }}
    [data-testid="stMetric"] {{
      background: var(--sentinel-panel);
      border: 1px solid var(--sentinel-border);
      border-radius: 9px;
      box-shadow: var(--sentinel-shadow);
      padding: .62rem .85rem;
      min-height: 88px;
    }}
    [data-testid="stMetricLabel"] {{ color: var(--sentinel-muted) !important; }}
    [data-testid="stMetricValue"] {{ color: var(--sentinel-accent) !important; }}
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"] p {{ color: var(--sentinel-accent) !important; }}
    div.stButton > button[kind="primary"],
    div.stButton > button[kind="secondary"],
    div.stDownloadButton > button {{
      border: 1px solid var(--sentinel-accent-strong);
      border-radius: 6px;
      background: var(--sentinel-accent-strong);
      color: var(--sentinel-button-text);
      font-weight: 650;
    }}
    div.stButton > button[kind="primary"] p,
    div.stButton > button[kind="secondary"] p,
    div.stDownloadButton > button p {{
      color: var(--sentinel-button-text) !important;
    }}
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[kind="secondary"]:hover,
    div.stDownloadButton > button:hover {{
      border-color: var(--sentinel-accent);
      background: var(--sentinel-accent);
      color: #ffffff;
    }}
    div.stButton > button[kind="primary"]:hover p,
    div.stButton > button[kind="secondary"]:hover p,
    div.stDownloadButton > button:hover p {{ color: var(--sentinel-button-text) !important; }}
    div.stButton > button[kind="primary"]:focus-visible,
    div.stButton > button[kind="secondary"]:focus-visible,
    div.stDownloadButton > button:focus-visible {{
      outline: 2px solid var(--sentinel-blue);
      outline-offset: 2px;
    }}
    div.stButton > button:disabled,
    div.stButton > button[disabled] {{
      border-color: var(--sentinel-border);
      background: var(--sentinel-elevated);
      color: var(--sentinel-muted);
      opacity: 1;
    }}
    div.stButton > button:disabled p,
    div.stButton > button[disabled] p {{ color: var(--sentinel-muted) !important; }}
    [data-testid="stFileUploader"] section {{
      background: var(--sentinel-panel) !important;
      border: 1px dashed var(--sentinel-border);
      border-radius: 7px;
    }}
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section * {{ color: var(--sentinel-muted) !important; }}
    [data-testid="stFileUploader"] section button {{
      background: var(--sentinel-panel-alt);
      border-color: var(--sentinel-border);
    }}
    [data-testid="stFileUploader"] [data-testid="stFileChip"] {{
      background: var(--sentinel-elevated) !important;
      border: 1px solid var(--sentinel-border);
      color: var(--sentinel-text) !important;
    }}
    [data-testid="stFileUploader"] [data-testid="stFileChipName"] {{
      color: var(--sentinel-text) !important;
    }}
    [data-testid="stFileUploader"] [data-testid="stFileChip"] button {{
      color: var(--sentinel-muted);
      background: transparent;
    }}
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] [role="group"] {{
      background: var(--sentinel-input) !important;
      color: var(--sentinel-text) !important;
      border-color: var(--sentinel-border) !important;
      border-radius: 6px;
    }}
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {{
      -webkit-text-fill-color: var(--sentinel-text) !important;
      opacity: 1 !important;
    }}
    [data-testid="stTextInput"] input:disabled,
    [data-testid="stNumberInput"] input:disabled {{
      background: var(--sentinel-elevated) !important;
      color: var(--sentinel-muted) !important;
      -webkit-text-fill-color: var(--sentinel-muted) !important;
      opacity: 1 !important;
    }}
    [data-testid="stNumberInput"] button {{
      background: var(--sentinel-elevated) !important;
      color: var(--sentinel-text) !important;
      border-color: var(--sentinel-border) !important;
    }}
    [data-testid="stNumberInput"] button:disabled {{
      color: var(--sentinel-muted) !important;
      opacity: 1 !important;
    }}
    [data-testid="stSelectbox"] input[role="combobox"] {{
      background: transparent !important;
      color: var(--sentinel-text) !important;
      -webkit-text-fill-color: var(--sentinel-text) !important;
    }}
    [data-testid="stSelectbox"] [role="group"] button {{
      background: transparent;
      color: var(--sentinel-text);
      border-color: transparent;
    }}
    [role="listbox"], [role="option"] {{ color: var(--sentinel-text); }}
    [data-testid="stAlert"] {{ border-radius: 7px; }}
    [data-testid="stAlert"] p {{ color: var(--sentinel-text) !important; }}
    [data-testid="stAlert"][kind="success"] {{
      background: color-mix(in srgb, var(--sentinel-success) 12%, var(--sentinel-panel));
      border-color: color-mix(in srgb, var(--sentinel-success) 40%, var(--sentinel-border));
    }}
    [data-testid="stAlert"][kind="warning"] {{
      background: color-mix(in srgb, var(--sentinel-warning) 12%, var(--sentinel-panel));
      border-color: color-mix(in srgb, var(--sentinel-warning) 40%, var(--sentinel-border));
    }}
    [data-testid="stAlert"][kind="error"] {{
      background: color-mix(in srgb, var(--sentinel-error) 12%, var(--sentinel-panel));
      border-color: color-mix(in srgb, var(--sentinel-error) 40%, var(--sentinel-border));
    }}
    [data-testid="stTabs"] [data-testid="stTab"] {{ color: var(--sentinel-muted) !important; }}
    [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {{
      color: var(--sentinel-accent) !important;
      border-bottom-color: var(--sentinel-accent) !important;
    }}
    [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p {{
      color: var(--sentinel-accent) !important;
    }}
    [data-testid="stTabs"] .react-aria-SelectionIndicator {{ background: var(--sentinel-accent) !important; }}
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .sentinel-chart-card-marker) {{
      min-height: 380px;
      padding: .8rem !important;
      background: var(--sentinel-panel) !important;
      border: 1px solid var(--sentinel-border) !important;
      border-radius: 9px;
      box-shadow: var(--sentinel-shadow);
    }}
    .sentinel-chart-card-marker {{ display:none; }}
    .sentinel-wordmark {{ display:flex; align-items:center; gap:.65rem; }}
    .sentinel-mark {{
      width:36px; height:36px; display:grid; place-items:center;
      background:var(--sentinel-panel); border:1px solid var(--sentinel-border);
      border-radius:8px; color:var(--sentinel-accent);
    }}
    .sentinel-name {{ color:var(--sentinel-text); font-weight:750; letter-spacing:.11em; font-size:1.1rem; }}
    .sentinel-tagline {{ color:var(--sentinel-muted); font-size:.77rem; margin-top:.08rem; }}
    .sentinel-overline {{
      color:var(--sentinel-accent); text-transform:uppercase;
      font-size:.67rem; font-weight:750; letter-spacing:.12em;
    }}
    .sentinel-section-heading {{
      color:var(--sentinel-text); font-size:1rem; font-weight:680;
      margin:0 0 .2rem;
    }}
    .sentinel-chart-subtitle {{ color:var(--sentinel-muted); font-size:.76rem; margin-bottom:.25rem; }}
    .sentinel-panel {{
      background:var(--sentinel-panel); border:1px solid var(--sentinel-border);
      border-radius:8px; padding:.8rem .9rem; box-shadow:var(--sentinel-shadow);
    }}
    .sentinel-intro {{
      color:var(--sentinel-muted); font-size:.87rem; line-height:1.5;
      background:var(--sentinel-panel); border:1px solid var(--sentinel-border);
      border-left:3px solid var(--sentinel-accent); border-radius:7px;
      padding:.7rem .85rem; margin:.3rem 0 .7rem;
    }}
    .sentinel-intro strong {{ color:var(--sentinel-text); font-weight:650; }}
    .sentinel-status {{
      display:inline-flex; align-items:center; gap:.4rem; white-space:nowrap;
      color:var(--sentinel-muted); background:var(--sentinel-panel);
      border:1px solid var(--sentinel-border); border-radius:99px;
      padding:.35rem .6rem; font-size:.74rem;
    }}
    .sentinel-status-dot {{ width:7px; height:7px; border-radius:50%; background:var(--sentinel-accent); }}
    .sentinel-status[data-state="success"] .sentinel-status-dot {{ background:var(--sentinel-success); }}
    .sentinel-status[data-state="warning"] .sentinel-status-dot {{ background:var(--sentinel-warning); }}
    .sentinel-sidebar-group {{
      color:var(--sentinel-accent); font-size:.68rem; letter-spacing:.11em;
      font-weight:750; text-transform:uppercase; margin:.75rem 0 .3rem;
      padding-bottom:.28rem; border-bottom:1px solid var(--sentinel-border);
    }}
    .sentinel-file {{
      color:var(--sentinel-text); background:var(--sentinel-panel);
      border:1px solid var(--sentinel-border); border-radius:6px;
      padding:.48rem .55rem; font-size:.78rem; overflow-wrap:anywhere;
    }}
    .sentinel-empty {{
      min-height:150px; display:flex; flex-direction:column; justify-content:center;
      background:var(--sentinel-panel-alt); border:1px dashed var(--sentinel-border);
      border-radius:7px; padding:1rem; color:var(--sentinel-muted);
    }}
    .sentinel-empty-mark {{
      display:flex; align-items:center; gap:.55rem; margin-bottom:.4rem;
      color:var(--sentinel-accent); font-size:.73rem; font-weight:700;
      letter-spacing:.09em; text-transform:uppercase;
    }}
    .sentinel-empty-mark svg {{ width:18px; height:18px; flex:none; }}
    .sentinel-table-wrap {{
      width:100%; overflow:auto; border:1px solid var(--sentinel-border);
      border-radius:7px; background:var(--sentinel-panel);
    }}
    table.sentinel-results-table {{
      width:100%; border-collapse:separate; border-spacing:0;
      color:var(--sentinel-text); font-size:.83rem;
    }}
    .sentinel-results-table thead th {{
      position:sticky; top:0; z-index:1; padding:.62rem .72rem;
      color:var(--sentinel-muted); background:var(--sentinel-table-head);
      border-bottom:1px solid var(--sentinel-border); text-align:left;
      font-size:.7rem; font-weight:700; letter-spacing:.045em;
      text-transform:uppercase; white-space:nowrap;
    }}
    .sentinel-results-table tbody td {{
      padding:.58rem .72rem; background:var(--sentinel-table-row);
      color:var(--sentinel-text); border-bottom:1px solid var(--sentinel-border);
      vertical-align:top;
    }}
    .sentinel-results-table tbody tr:nth-child(even) td {{ background:var(--sentinel-table-alt); }}
    .sentinel-results-table tbody tr:hover td {{ background:var(--sentinel-elevated); }}
    .sentinel-results-table tbody tr:last-child td {{ border-bottom:0; }}
    .sentinel-results-table td.sentinel-text-cell {{
      min-width:150px; max-width:460px; overflow-wrap:anywhere; white-space:normal;
    }}
    .sentinel-results-table td.sentinel-number-cell {{
      min-width:88px; text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap;
    }}
    .sentinel-table-footer {{
      display:flex; justify-content:space-between; gap:1rem; align-items:center;
      margin-top:.4rem; color:var(--sentinel-muted); font-size:.75rem;
    }}
    @media (max-width: 760px) {{
      .block-container {{ padding:2.6rem .8rem 1.4rem; }}
    }}
    </style>
    """
    st.markdown(st_css, unsafe_allow_html=True)


def plotly_layout(theme, *, height=290, x_title=None, y_title=None, show_legend=False):
    colors = THEMES[theme]
    template = "plotly_white" if theme == "Light" else "plotly_dark"
    return {
        "template": template,
        "paper_bgcolor": colors["panel"],
        "plot_bgcolor": colors["panel"],
        "font": {"family": "Inter, Arial, sans-serif", "color": colors["text"], "size": 11},
        "margin": {"l": 12, "r": 12, "t": 8, "b": 12},
        "height": height,
        "showlegend": show_legend,
        "hoverlabel": {
            "bgcolor": colors["chart_hover"],
            "bordercolor": colors["border"],
            "font": {"color": colors["text"], "family": "Inter, Arial, sans-serif"},
        },
        "xaxis": {
            "title": {"text": x_title, "font": {"color": colors["muted"], "size": 10}},
            "tickfont": {"color": colors["muted"], "size": 10},
            "gridcolor": colors["chart_grid"],
            "linecolor": colors["border"],
            "zerolinecolor": colors["chart_grid"],
            "showline": False,
        },
        "yaxis": {
            "title": {"text": y_title, "font": {"color": colors["muted"], "size": 10}},
            "tickfont": {"color": colors["muted"], "size": 10},
            "gridcolor": colors["chart_grid"],
            "linecolor": colors["border"],
            "zerolinecolor": colors["chart_grid"],
            "showline": False,
        },
        "legend": {
            "font": {"color": colors["muted"], "size": 10},
            "bgcolor": colors["panel"],
            "bordercolor": colors["border"],
        },
    }


def distribution_figure(distribution, theme, *, max_categories=8):
    colors = THEMES[theme]
    items = sorted(distribution.items(), key=lambda item: item[1], reverse=True)[:max_categories]
    labels = [label for label, _ in reversed(items)]
    counts = [count for _, count in reversed(items)]
    figure = go.Figure(
        go.Bar(
            x=counts,
            y=labels,
            orientation="h",
            marker={"color": colors["accent"], "line": {"width": 0}},
            customdata=labels,
            hovertemplate="%{customdata}<br>Records: %{x:,}<extra></extra>",
        )
    )
    figure.update_layout(**plotly_layout(theme, height=265, x_title="Records"))
    figure.update_xaxes(tickformat=",d", rangemode="tozero")
    figure.update_yaxes(automargin=True, showgrid=False)
    return figure


def itemset_size_figure(itemsets, theme):
    colors = THEMES[theme]
    counts = itemsets["Itemset size"].value_counts().sort_index()
    figure = go.Figure(
        go.Bar(
            x=[str(value) for value in counts.index],
            y=counts.values,
            marker={"color": colors["accent"], "line": {"width": 0}},
            customdata=counts.index,
            hovertemplate="Itemset size: %{customdata}<br>Itemsets: %{y:,}<extra></extra>",
        )
    )
    figure.update_layout(
        **plotly_layout(theme, height=265, x_title="Items per set", y_title="Frequent itemsets")
    )
    figure.update_yaxes(tickformat=",d", rangemode="tozero")
    figure.update_xaxes(showgrid=False)
    return figure


def top_rules_figure(rules, theme, *, limit=6):
    colors = THEMES[theme]
    ranked = rules.nlargest(limit, "Lift").sort_values("Lift", ascending=True).copy()
    full_labels = [
        f"{antecedents} → {consequents}"
        for antecedents, consequents in zip(ranked["Antecedents"], ranked["Consequents"])
    ]
    labels = [
        label if len(label) <= 52 else f"{label[:49]}…"
        for label in full_labels
    ]
    figure = go.Figure(
        go.Bar(
            x=ranked["Lift"],
            y=labels,
            orientation="h",
            marker={"color": colors["blue"], "line": {"width": 0}},
            customdata=[
                [label, support, confidence]
                for label, support, confidence in zip(
                    full_labels, ranked["Support"], ranked["Confidence"]
                )
            ],
            hovertemplate=(
                "%{customdata[0]}<br>Lift: %{x:.3f}"
                "<br>Support: %{customdata[1]:.3f}"
                "<br>Confidence: %{customdata[2]:.3f}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        **plotly_layout(theme, height=265, x_title="Lift")
    )
    figure.update_xaxes(rangemode="tozero")
    figure.update_yaxes(automargin=True, showgrid=False, tickfont={"size": 9})
    return figure


def support_confidence_figure(rules, theme, *, limit=1000):
    colors = THEMES[theme]
    points = rules.nlargest(limit, "Lift")
    rule_labels = [
        f"{antecedents} → {consequents}"
        for antecedents, consequents in zip(points["Antecedents"], points["Consequents"])
    ]
    varying_lift = points["Lift"].nunique(dropna=True) > 1
    figure = go.Figure(
        go.Scatter(
            x=points["Support"],
            y=points["Confidence"],
            mode="markers",
            marker={
                "size": 8,
                "opacity": 0.78,
                "color": points["Lift"] if varying_lift else colors["accent"],
                "colorscale": "Teal" if theme == "Light" else "Tealgrn",
                "showscale": varying_lift,
                "colorbar": {
                    "title": {"text": "Lift", "font": {"color": colors["muted"], "size": 10}},
                    "tickfont": {"color": colors["muted"], "size": 9},
                    "outlinecolor": colors["border"],
                    "thickness": 9,
                },
            },
            customdata=list(
                zip(
                    rule_labels,
                    points["Lift"],
                    points["Support"],
                    points["Confidence"],
                )
            ),
            hovertemplate=(
                "%{customdata[0]}<br>Support: %{customdata[2]:.3f}"
                "<br>Confidence: %{customdata[3]:.3f}"
                "<br>Lift: %{customdata[1]:.3f}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        **plotly_layout(theme, height=265, x_title="Support", y_title="Confidence")
    )
    figure.update_xaxes(rangemode="tozero")
    figure.update_yaxes(range=[0, 1])
    return figure
