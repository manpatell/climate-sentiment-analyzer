"""Single-text Analyzer page.

Lets users paste any climate-related text and see a full sentiment breakdown
with an interactive Plotly gauge, score bars, and highlighted climate keywords.
"""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.climate_analyzer.analyzer import ClimateAnalyzer
from src.climate_analyzer.data import SAMPLE_ARTICLES

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Analyzer · Climate Sentiment", page_icon="📝", layout="wide")

with st.sidebar:
    st.markdown("## 🌍 Climate Sentiment")
    st.markdown("---")
    st.page_link("app.py", label="Overview", icon="🏠")
    st.page_link("pages/1_Analyzer.py", label="Analyzer", icon="📝")
    st.page_link("pages/2_Batch.py", label="Batch Analysis", icon="📊")
    st.page_link("pages/3_Trends.py", label="Trends", icon="📈")

# ── Analyzer singleton ────────────────────────────────────────────────────────
@st.cache_resource
def get_analyzer() -> ClimateAnalyzer:
    return ClimateAnalyzer()

analyzer = get_analyzer()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📝 Single-Text Analyzer")
st.markdown("Paste any climate news article, report, or statement to get a full NLP breakdown.")
st.divider()

# ── Input section ─────────────────────────────────────────────────────────────
col_input, col_sample = st.columns([3, 1])

with col_sample:
    st.markdown("**Quick-load a sample:**")
    sample_titles = [a.title for a in SAMPLE_ARTICLES]
    chosen = st.selectbox("", ["— select —"] + sample_titles, label_visibility="collapsed")
    if chosen != "— select —":
        article = next(a for a in SAMPLE_ARTICLES if a.title == chosen)
        st.session_state["analyzer_text"] = article.body

with col_input:
    text_input = st.text_area(
        "Input text",
        value=st.session_state.get("analyzer_text", ""),
        height=180,
        placeholder="Paste any climate-related text here…",
        label_visibility="collapsed",
    )

run = st.button("Analyze", type="primary", use_container_width=False)

# ── Results ───────────────────────────────────────────────────────────────────
if run and text_input.strip():
    try:
        result = analyzer.analyze(text_input.strip())
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.divider()

    # — Sentiment badge row
    badge_color = result.sentiment_color
    badge_label = result.label
    badge_score = result.score

    b1, b2, b3, b4 = st.columns(4)
    b1.markdown(
        f"<div style='background:{badge_color};border-radius:12px;padding:16px 24px;"
        f"text-align:center;color:white;font-size:1.4rem;font-weight:700'>"
        f"{result.sentiment_emoji} {badge_label}</div>",
        unsafe_allow_html=True,
    )
    b2.metric("Compound Score", f"{badge_score:+.4f}")
    b3.metric("Confidence", f"{result.confidence:.1%}")
    b4.metric("Climate Keywords Found", len(set(result.climate_keywords)))

    st.markdown("")

    # — Gauge + Score breakdown
    gauge_col, bars_col = st.columns([1, 1])

    with gauge_col:
        st.markdown("**Sentiment Gauge**")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=badge_score,
            delta={"reference": 0, "valueformat": ".3f"},
            number={"valueformat": "+.3f"},
            gauge={
                "axis": {"range": [-1, 1], "tickwidth": 1},
                "bar": {"color": badge_color, "thickness": 0.25},
                "steps": [
                    {"range": [-1, -0.05], "color": "#FDECEA"},
                    {"range": [-0.05, 0.05], "color": "#FEF9E7"},
                    {"range": [0.05, 1], "color": "#E9F7EF"},
                ],
                "threshold": {
                    "line": {"color": badge_color, "width": 4},
                    "thickness": 0.75,
                    "value": badge_score,
                },
            },
        ))
        fig_gauge.update_layout(height=280, margin=dict(t=30, b=0, l=30, r=30))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with bars_col:
        st.markdown("**Positive / Neutral / Negative Breakdown**")
        fig_scores = go.Figure()
        components = [
            ("Positive", result.positive_score, "#2ECC71"),
            ("Neutral", result.neutral_score, "#95A5A6"),
            ("Negative", result.negative_score, "#E74C3C"),
        ]
        for name, val, color in components:
            fig_scores.add_trace(go.Bar(
                name=name,
                x=[val],
                y=[name],
                orientation="h",
                marker_color=color,
                text=f"{val:.1%}",
                textposition="outside",
                hovertemplate=f"{name}: {{x:.1%}}<extra></extra>",
            ))
        fig_scores.update_layout(
            showlegend=False,
            xaxis=dict(range=[0, 1], tickformat=".0%"),
            height=280,
            margin=dict(t=30, b=0, l=10, r=60),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            barmode="overlay",
        )
        st.plotly_chart(fig_scores, use_container_width=True)

    # — Climate keywords section
    st.markdown("**Climate Keywords Detected**")
    unique_kws = sorted(set(result.climate_keywords))
    if unique_kws:
        kw_density_pct = f"{result.keyword_density:.1%}"
        st.markdown(
            " ".join(
                f"<span style='background:#1A5276;color:white;border-radius:6px;"
                f"padding:3px 10px;margin:3px;font-size:0.85rem'>{kw}</span>"
                for kw in unique_kws
            ),
            unsafe_allow_html=True,
        )
        st.caption(
            f"Keyword density: **{kw_density_pct}** · "
            f"Word count: **{result.word_count}** words"
        )
    else:
        st.info("No climate-specific keywords detected in this text.")

elif run:
    st.warning("Please enter some text before analyzing.")
else:
    st.info("👆 Enter text above and click **Analyze** to get started.")
