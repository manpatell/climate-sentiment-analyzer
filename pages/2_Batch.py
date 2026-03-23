"""Batch Analysis page.

Analyze multiple climate articles simultaneously. Supports sample dataset
selection, interactive filtering, and CSV export.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.climate_analyzer.analyzer import ClimateAnalyzer
from src.climate_analyzer.data import CATEGORIES, REGIONS, SAMPLE_ARTICLES

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Batch Analysis · Climate Sentiment", page_icon="📊", layout="wide")

with st.sidebar:
    st.markdown("## 🌍 Climate Sentiment")
    st.markdown("---")
    st.page_link("app.py", label="Overview", icon="🏠")
    st.page_link("pages/1_Analyzer.py", label="Analyzer", icon="📝")
    st.page_link("pages/2_Batch.py", label="Batch Analysis", icon="📊")
    st.page_link("pages/3_Trends.py", label="Trends", icon="📈")
    st.markdown("---")
    st.markdown("**Filters**")
    sel_categories = st.multiselect("Category", CATEGORIES, default=CATEGORIES)
    sel_regions = st.multiselect("Region", REGIONS, default=REGIONS)
    min_score, max_score = st.slider("Score range", -1.0, 1.0, (-1.0, 1.0), 0.05)


@st.cache_resource
def get_analyzer() -> ClimateAnalyzer:
    return ClimateAnalyzer()

analyzer = get_analyzer()

# ── Analyze all sample articles once ─────────────────────────────────────────
@st.cache_data(show_spinner=False)
def analyze_all() -> pd.DataFrame:
    results = [analyzer.analyze_article(a) for a in SAMPLE_ARTICLES]
    records = []
    for r, a in zip(results, SAMPLE_ARTICLES):
        d = r.to_dict()
        d["category"] = a.category
        d["region"] = a.region
        d["published"] = a.published_at.strftime("%b %d, %Y")
        records.append(d)
    df = pd.DataFrame(records)
    df["analyzed_at"] = pd.to_datetime(df["analyzed_at"])
    return df

full_df = analyze_all()

# ── Apply sidebar filters ─────────────────────────────────────────────────────
df = full_df[
    full_df["category"].isin(sel_categories)
    & full_df["region"].isin(sel_regions)
    & full_df["score"].between(min_score, max_score)
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Batch Analysis")
st.markdown(
    f"Comparing **{len(df)}** of {len(full_df)} articles after filters. "
    "Use the sidebar to narrow by category, region, or score range."
)
st.divider()

if df.empty:
    st.warning("No articles match the current filters. Adjust the sidebar selections.")
    st.stop()

# ── KPI strip ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
color_map = {"Positive": "#2ECC71", "Neutral": "#F39C12", "Negative": "#E74C3C"}
k1.metric("Articles", len(df))
k2.metric("Avg Score", f"{df['score'].mean():+.3f}")
k3.metric("Most Positive", df.loc[df["score"].idxmax(), "source"][:28])
k4.metric("Most Negative", df.loc[df["score"].idxmin(), "source"][:28])

st.divider()

# ── Scatter: Score vs Keyword Density ────────────────────────────────────────
col_l, col_r = st.columns([3, 2])

with col_l:
    st.subheader("Score vs Climate Keyword Density")
    fig_scatter = px.scatter(
        df,
        x="keyword_density",
        y="score",
        color="label",
        color_discrete_map=color_map,
        symbol="category",
        size="word_count",
        size_max=20,
        hover_name="source",
        hover_data={"score": ":.3f", "keyword_density": ":.1%",
                    "word_count": True, "category": True, "region": True},
        labels={
            "keyword_density": "Climate Keyword Density",
            "score": "Compound Sentiment Score",
            "label": "Sentiment",
        },
    )
    fig_scatter.add_hline(y=0.05, line_dash="dot", line_color="#2ECC71", line_width=1)
    fig_scatter.add_hline(y=-0.05, line_dash="dot", line_color="#E74C3C", line_width=1)
    fig_scatter.update_layout(
        height=360,
        margin=dict(t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_scatter, width="stretch")

with col_r:
    st.subheader("Sentiment Distribution")
    label_counts = df["label"].value_counts().reset_index()
    label_counts.columns = ["label", "count"]
    fig_pie = px.pie(
        label_counts,
        names="label",
        values="count",
        hole=0.5,
        color="label",
        color_discrete_map=color_map,
    )
    fig_pie.update_traces(textinfo="label+percent")
    fig_pie.update_layout(
        showlegend=False,
        height=360,
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_pie, width="stretch")

# ── Horizontal bar chart ──────────────────────────────────────────────────────
st.subheader("Sentiment Scores — All Selected Articles")
df_sorted = df.sort_values("score")
colors = df_sorted["label"].map(color_map)
fig_bar = go.Figure(go.Bar(
    x=df_sorted["score"],
    y=df_sorted["source"],
    orientation="h",
    marker_color=colors,
    hovertemplate="<b>%{y}</b><br>Score: %{x:.3f}<extra></extra>",
))
fig_bar.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1)
fig_bar.update_layout(
    xaxis_title="Compound Sentiment Score",
    yaxis_title=None,
    height=max(300, len(df_sorted) * 28),
    margin=dict(t=10, b=10, l=10, r=10),
    xaxis=dict(range=[-1, 1]),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_bar, width="stretch")

# ── Data table ────────────────────────────────────────────────────────────────
st.subheader("Results Table")
display_cols = ["source", "category", "region", "label", "score",
                "confidence", "keyword_density", "word_count", "published"]
st.dataframe(
    df[display_cols].rename(columns={
        "source": "Article",
        "category": "Category",
        "region": "Region",
        "label": "Sentiment",
        "score": "Score",
        "confidence": "Confidence",
        "keyword_density": "Keyword Density",
        "word_count": "Words",
        "published": "Published",
    }),
    use_container_width=True,
    hide_index=True,
)

# ── Export ────────────────────────────────────────────────────────────────────
csv_buf = io.StringIO()
df[display_cols].to_csv(csv_buf, index=False)
st.download_button(
    label="⬇ Export to CSV",
    data=csv_buf.getvalue(),
    file_name="climate_sentiment_results.csv",
    mime="text/csv",
)
