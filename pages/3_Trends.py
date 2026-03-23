"""Temporal Trends page.

Shows how climate news sentiment evolves over the sample dataset's timeline,
with rolling averages, category breakdowns, and annotated climate events.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.climate_analyzer.analyzer import ClimateAnalyzer
from src.climate_analyzer.data import SAMPLE_ARTICLES

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Trends · Climate Sentiment", page_icon="📈", layout="wide")

with st.sidebar:
    st.markdown("## 🌍 Climate Sentiment")
    st.markdown("---")
    st.page_link("app.py", label="Overview", icon="🏠")
    st.page_link("pages/1_Analyzer.py", label="Analyzer", icon="📝")
    st.page_link("pages/2_Batch.py", label="Batch Analysis", icon="📊")
    st.page_link("pages/3_Trends.py", label="Trends", icon="📈")
    st.markdown("---")
    st.markdown("**Options**")
    window = st.slider("Rolling average window (articles)", 2, 6, 3)
    show_events = st.checkbox("Show climate event markers", value=True)
    color_by = st.radio("Color series by", ["Sentiment label", "Category"])


@st.cache_resource
def get_analyzer() -> ClimateAnalyzer:
    return ClimateAnalyzer()

analyzer = get_analyzer()


@st.cache_data(show_spinner=False)
def build_trend_df() -> pd.DataFrame:
    records = []
    for a in SAMPLE_ARTICLES:
        r = analyzer.analyze_article(a)
        records.append({
            "date": a.published_at,
            "title": a.title,
            "short_title": a.short_title,
            "category": a.category,
            "region": a.region,
            "score": r.score,
            "label": r.label,
            "confidence": r.confidence,
            "keyword_density": r.keyword_density,
        })
    df = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
    df["rolling_avg"] = df["score"].rolling(window=3, min_periods=1).mean()
    return df


trend_df = build_trend_df()

# Recompute rolling avg with selected window
trend_df["rolling_avg"] = trend_df["score"].rolling(window=window, min_periods=1).mean()

# Notable climate events for annotation
EVENTS = [
    {"date": "2025-09-22", "label": "UNGA Climate Week"},
    {"date": "2025-10-15", "label": "Arctic ice record"},
    {"date": "2025-11-01", "label": "COP30 opens"},
    {"date": "2025-12-01", "label": "EU deforestation law"},
]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📈 Sentiment Trends")
st.markdown(
    "Track how climate news sentiment shifts over time. "
    "Data spans 18 articles from September 2025 to January 2026."
)
st.divider()

# ── KPI strip ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Time span", "~4 months")
k2.metric("Trend direction",
          "↑ Improving" if trend_df["rolling_avg"].iloc[-1] > trend_df["rolling_avg"].iloc[0]
          else "↓ Declining")
k3.metric("Peak positive", trend_df.loc[trend_df["score"].idxmax(), "short_title"][:28])
k4.metric("Peak negative", trend_df.loc[trend_df["score"].idxmin(), "short_title"][:28])

st.divider()

# ── Main time-series chart ────────────────────────────────────────────────────
st.subheader("Sentiment Over Time")

color_map = {"Positive": "#2ECC71", "Neutral": "#F39C12", "Negative": "#E74C3C"}
cat_colors = {
    "Technology": "#3498DB",
    "Policy": "#9B59B6",
    "Science": "#E67E22",
    "Impact": "#E74C3C",
}

color_col = "label" if color_by == "Sentiment label" else "category"
cmap = color_map if color_by == "Sentiment label" else cat_colors

fig_line = px.scatter(
    trend_df,
    x="date",
    y="score",
    color=color_col,
    color_discrete_map=cmap,
    size="confidence",
    size_max=14,
    hover_name="title",
    hover_data={
        "score": ":.3f",
        "confidence": ":.1%",
        "keyword_density": ":.1%",
        "category": True,
        "region": True,
        color_col: False,
    },
    labels={"score": "Sentiment Score", "date": "Publication Date"},
)

# Rolling average line
fig_line.add_trace(go.Scatter(
    x=trend_df["date"],
    y=trend_df["rolling_avg"],
    mode="lines",
    name=f"{window}-article rolling avg",
    line=dict(color="#2C3E50", width=2.5, dash="solid"),
    hovertemplate="Rolling avg: %{y:.3f}<extra></extra>",
))

# Sentiment band
fig_line.add_hrect(y0=0.05, y1=1, fillcolor="#2ECC71", opacity=0.04, line_width=0)
fig_line.add_hrect(y0=-1, y1=-0.05, fillcolor="#E74C3C", opacity=0.04, line_width=0)
fig_line.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
fig_line.add_hline(y=0.05, line_dash="dot", line_color="#2ECC71", line_width=0.8)
fig_line.add_hline(y=-0.05, line_dash="dot", line_color="#E74C3C", line_width=0.8)

# Climate event annotations
if show_events:
    for event in EVENTS:
        fig_line.add_vline(
            x=event["date"],
            line_dash="dot",
            line_color="#7F8C8D",
            line_width=1.5,
            annotation_text=event["label"],
            annotation_position="top right",
            annotation_font_size=10,
            annotation_font_color="#7F8C8D",
        )

fig_line.update_layout(
    height=420,
    margin=dict(t=20, b=20),
    yaxis=dict(range=[-1, 1], title="Compound Sentiment Score"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_line, use_container_width=True)

# ── Category breakdown over time ──────────────────────────────────────────────
st.subheader("Avg Score by Category Over Time")

cat_monthly = (
    trend_df.assign(month=trend_df["date"].dt.to_period("M").astype(str))
    .groupby(["month", "category"])["score"]
    .mean()
    .reset_index()
)

fig_cat = px.line(
    cat_monthly,
    x="month",
    y="score",
    color="category",
    color_discrete_map=cat_colors,
    markers=True,
    labels={"score": "Avg Score", "month": "Month", "category": "Category"},
)
fig_cat.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
fig_cat.update_layout(
    height=300,
    margin=dict(t=10, b=10),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_cat, use_container_width=True)

# ── Confidence vs Score scatter ───────────────────────────────────────────────
st.subheader("Confidence vs Score")
fig_conf = px.scatter(
    trend_df,
    x="score",
    y="confidence",
    color="label",
    color_discrete_map=color_map,
    hover_name="title",
    trendline="ols",
    trendline_scope="overall",
    labels={"score": "Compound Score", "confidence": "Model Confidence", "label": "Sentiment"},
)
fig_conf.update_layout(
    height=280,
    margin=dict(t=10, b=10),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_conf, use_container_width=True)
