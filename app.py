"""Climate Sentiment Analyzer — Overview Dashboard.

Entry point for the Streamlit multi-page application.
Displays a high-level summary of sentiment across the full sample dataset.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure the src package is importable when running with `streamlit run app.py`
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.climate_analyzer.analyzer import ClimateAnalyzer
from src.climate_analyzer.data import SAMPLE_ARTICLES

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Climate Sentiment Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Climate Sentiment")
    st.markdown("---")
    st.markdown(
        "Analyze sentiment in climate & sustainability news using an NLP pipeline "
        "built on VADER with a domain-specific climate lexicon."
    )
    st.markdown("---")
    st.markdown("**Navigate**")
    st.page_link("app.py", label="Overview", icon="🏠")
    st.page_link("pages/1_Analyzer.py", label="Analyzer", icon="📝")
    st.page_link("pages/2_Batch.py", label="Batch Analysis", icon="📊")
    st.page_link("pages/3_Trends.py", label="Trends", icon="📈")
    st.markdown("---")
    st.caption("Built with Streamlit · VADER NLP")


# ── Cached analysis ──────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_full_analysis() -> tuple[list, pd.DataFrame]:
    analyzer = ClimateAnalyzer()
    results = [analyzer.analyze_article(a) for a in SAMPLE_ARTICLES]
    df = pd.DataFrame([r.to_dict() | {"category": a.category, "region": a.region}
                       for r, a in zip(results, SAMPLE_ARTICLES)])
    df["analyzed_at"] = pd.to_datetime(df["analyzed_at"])
    return results, df


results, df = run_full_analysis()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 🌍 Climate Sentiment Analyzer")
st.markdown(
    "Real-time NLP analysis of climate & sustainability news. "
    "Powered by VADER with a custom climate domain lexicon."
)
st.divider()

# ── KPI Row ──────────────────────────────────────────────────────────────────
pos_count = (df["label"] == "Positive").sum()
neg_count = (df["label"] == "Negative").sum()
neu_count = (df["label"] == "Neutral").sum()
avg_score = df["score"].mean()
avg_kd = df["keyword_density"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Articles Analyzed", len(df))
k2.metric("Positive", int(pos_count), delta=f"{pos_count/len(df)*100:.0f}%")
k3.metric("Negative", int(neg_count), delta=f"-{neg_count/len(df)*100:.0f}%", delta_color="inverse")
k4.metric("Avg Sentiment Score", f"{avg_score:+.3f}")
k5.metric("Avg Keyword Density", f"{avg_kd:.1%}")

st.divider()

# ── Row 1: Donut + Bar ────────────────────────────────────────────────────────
col_l, col_r = st.columns([1, 2])

with col_l:
    st.subheader("Sentiment Distribution")
    counts = df["label"].value_counts().reset_index()
    counts.columns = ["label", "count"]
    color_map = {"Positive": "#2ECC71", "Neutral": "#F39C12", "Negative": "#E74C3C"}
    fig_donut = px.pie(
        counts,
        names="label",
        values="count",
        hole=0.55,
        color="label",
        color_discrete_map=color_map,
    )
    fig_donut.update_traces(textinfo="label+percent", pull=[0.03, 0.03, 0.03])
    fig_donut.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=300,
    )
    st.plotly_chart(fig_donut, width="stretch")

with col_r:
    st.subheader("Sentiment Score by Article")
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
    fig_bar.add_vline(x=0.05, line_dash="dot", line_color="#2ECC71", line_width=0.8)
    fig_bar.add_vline(x=-0.05, line_dash="dot", line_color="#E74C3C", line_width=0.8)
    fig_bar.update_layout(
        xaxis_title="Compound Sentiment Score",
        yaxis_title=None,
        margin=dict(t=10, b=10, l=10, r=10),
        height=380,
        xaxis=dict(range=[-1, 1]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_bar, width="stretch")

# ── Row 2: Category breakdown + Keyword frequency ────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Avg Score by Category")
    cat_df = df.groupby("category")["score"].mean().reset_index().sort_values("score")
    cat_df["color"] = cat_df["score"].apply(
        lambda s: "#2ECC71" if s > 0.05 else ("#E74C3C" if s < -0.05 else "#F39C12")
    )
    fig_cat = go.Figure(go.Bar(
        x=cat_df["score"],
        y=cat_df["category"],
        orientation="h",
        marker_color=cat_df["color"],
        hovertemplate="<b>%{y}</b><br>Avg Score: %{x:.3f}<extra></extra>",
    ))
    fig_cat.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1)
    fig_cat.update_layout(
        xaxis_title="Avg Compound Score",
        yaxis_title=None,
        height=260,
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_cat, width="stretch")

with col_b:
    st.subheader("Top Climate Keywords")
    from src.climate_analyzer.analyzer import ClimateAnalyzer as _CA
    _a = _CA()
    top_kw = _a.top_keywords(results, n=12)
    kw_df = pd.DataFrame(top_kw, columns=["keyword", "count"])
    fig_kw = px.bar(
        kw_df,
        x="count",
        y="keyword",
        orientation="h",
        color="count",
        color_continuous_scale="Tealgrn",
        labels={"count": "Frequency", "keyword": ""},
    )
    fig_kw.update_layout(
        height=260,
        margin=dict(t=10, b=10, l=10, r=10),
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_kw, width="stretch")

# ── Row 3: Region heatmap ─────────────────────────────────────────────────────
st.subheader("Sentiment by Region")
region_df = df.groupby("region")["score"].mean().reset_index()
fig_region = px.bar(
    region_df.sort_values("score"),
    x="region",
    y="score",
    color="score",
    color_continuous_scale=["#E74C3C", "#F39C12", "#2ECC71"],
    range_color=[-1, 1],
    labels={"score": "Avg Sentiment Score", "region": "Region"},
)
fig_region.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
fig_region.update_layout(
    height=250,
    margin=dict(t=10, b=10, l=10, r=10),
    coloraxis_showscale=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_region, width="stretch")

st.divider()
st.caption("Navigate to **Analyzer**, **Batch Analysis**, or **Trends** using the sidebar.")
