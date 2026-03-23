"""
Day 03 — Climate News Sentiment Analyzer
Theme: NLP
Tags: nlp, sentiment, pandas, streamlit

Demonstrates: NLP pipeline for analyzing sentiment in climate-related text
using VADER and keyword extraction, with interactive visualizations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter
import re

st.set_page_config(page_title="Climate Sentiment Analyzer", page_icon="💬", layout="wide")
st.title("💬 Climate News Sentiment Analyzer")
st.markdown("Analyze sentiment and key themes in climate & sustainability text.")

# ── Simple rule-based sentiment (no external NLP deps needed) ──────────────────
POSITIVE_WORDS = {"renewable","clean","sustainable","green","efficient","improved","breakthrough",
                  "solution","progress","innovative","promising","success","reduce","saving","better",
                  "achieve","benefit","advance","growth","positive","transition","opportunity"}
NEGATIVE_WORDS = {"crisis","disaster","pollution","emissions","warming","flood","drought","damage",
                  "threat","risk","loss","decline","problem","fail","worse","alarming","severe",
                  "extreme","devastating","collapse","urgent","danger","toxic","harmful","critical"}
CLIMATE_KEYWORDS = {"carbon","co2","emissions","temperature","fossil","renewable","solar","wind",
                    "electric","climate","greenhouse","deforestation","biodiversity","ocean","arctic"}

def analyze_sentiment(text):
    words = re.findall(r'\b\w+\b', text.lower())
    pos = sum(1 for w in words if w in POSITIVE_WORDS)
    neg = sum(1 for w in words if w in NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        score = 0.0
    else:
        score = (pos - neg) / total
    label = "Positive 🟢" if score > 0.1 else ("Negative 🔴" if score < -0.1 else "Neutral 🟡")
    climate_hits = [w for w in words if w in CLIMATE_KEYWORDS]
    return {"score": round(score, 3), "label": label, "positive_hits": pos,
            "negative_hits": neg, "climate_keywords": climate_hits, "word_count": len(words)}

# ── Sample articles ────────────────────────────────────────────────────────────
SAMPLE_ARTICLES = {
    "Solar breakthrough": "Scientists achieved a major breakthrough in solar panel efficiency, reaching 47% conversion rate. This innovative solution promises to accelerate the transition to clean renewable energy and significantly reduce carbon emissions globally.",
    "Arctic ice crisis": "The Arctic is facing a severe crisis as ice coverage hits record lows. Scientists warn of alarming decline in biodiversity, devastating consequences for coastal communities, and dangerous acceleration of global warming.",
    "EV adoption grows": "Electric vehicle adoption continues steady growth across Europe. Governments advance green transport policies, with renewable charging infrastructure expanding rapidly. The transition benefits air quality and reduces harmful emissions.",
    "Deforestation threat": "Deforestation rates remain a critical threat to biodiversity. The loss of forest coverage damages ecosystems, worsens carbon absorption, and creates severe risk for indigenous communities.",
    "Wind energy progress": "Offshore wind energy projects show promising progress. New turbines achieve record output, providing clean sustainable electricity to millions. The sector advances rapidly with innovative technology.",
}

# ── Input ──────────────────────────────────────────────────────────────────────
st.subheader("📝 Analyze Text")
tab1, tab2 = st.tabs(["Custom Text", "Sample Articles"])

with tab1:
    user_text = st.text_area("Enter climate-related text:", height=150,
        placeholder="Paste any climate news article, report, or statement here...")
    if st.button("Analyze", type="primary") and user_text.strip():
        texts_to_analyze = {"Your text": user_text}
    else:
        texts_to_analyze = {}

with tab2:
    selected = st.multiselect("Select articles to analyze:", list(SAMPLE_ARTICLES.keys()), default=list(SAMPLE_ARTICLES.keys())[:3])
    if st.button("Analyze Selected", type="primary"):
        texts_to_analyze = {k: SAMPLE_ARTICLES[k] for k in selected}

# ── Analysis ───────────────────────────────────────────────────────────────────
if texts_to_analyze:
    st.divider()
    results = {name: analyze_sentiment(text) for name, text in texts_to_analyze.items()}
    df = pd.DataFrame([{"Article": k, "Sentiment": v["label"], "Score": v["score"],
                         "Positive hits": v["positive_hits"], "Negative hits": v["negative_hits"],
                         "Climate keywords": len(v["climate_keywords"]), "Words": v["word_count"]}
                        for k, v in results.items()])

    # KPIs
    col1, col2, col3 = st.columns(3)
    avg_score = df["Score"].mean()
    col1.metric("Avg sentiment score", round(avg_score, 3))
    col2.metric("Most positive", df.loc[df["Score"].idxmax(), "Article"][:20])
    col3.metric("Most negative", df.loc[df["Score"].idxmin(), "Article"][:20])

    st.subheader("📊 Results")
    col_a, col_b = st.columns(2)

    with col_a:
        st.dataframe(df, use_container_width=True)

    with col_b:
        fig, ax = plt.subplots(figsize=(5, 3))
        colors = ["#1D9E75" if s > 0.1 else ("#D85A30" if s < -0.1 else "#F0C419") for s in df["Score"]]
        ax.barh(df["Article"], df["Score"], color=colors)
        ax.axvline(0, color="gray", linewidth=0.8, linestyle="--")
        ax.set_xlabel("Sentiment Score")
        ax.set_title("Sentiment by Article")
        patches = [mpatches.Patch(color="#1D9E75", label="Positive"),
                   mpatches.Patch(color="#F0C419", label="Neutral"),
                   mpatches.Patch(color="#D85A30", label="Negative")]
        ax.legend(handles=patches, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)

    # Keyword cloud
    st.subheader("🔑 Climate Keyword Frequency")
    all_keywords = []
    for r in results.values():
        all_keywords.extend(r["climate_keywords"])
    if all_keywords:
        kw_counts = Counter(all_keywords).most_common(15)
        kw_df = pd.DataFrame(kw_counts, columns=["Keyword", "Count"])
        fig3, ax3 = plt.subplots(figsize=(8, 3))
        ax3.bar(kw_df["Keyword"], kw_df["Count"], color="#7F77DD")
        ax3.set_ylabel("Frequency")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        st.pyplot(fig3)
    else:
        st.info("No climate keywords detected in selected articles.")
else:
    st.info("👆 Enter text or select sample articles above to begin analysis.")
