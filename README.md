# 🌍 Climate Sentiment Analyzer

[![CI](https://github.com/manpatell/climate-sentiment-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/manpatell/climate-sentiment-analyzer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.32%2B-FF4B4B)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

An NLP pipeline and interactive dashboard for real-time sentiment analysis of climate and sustainability news. Built with VADER and a custom domain-specific climate lexicon, visualized through a multi-page Streamlit dashboard with Plotly.

---

## Features

- **Domain-adapted NLP** — VADER extended with 40+ climate-specific lexicon entries (e.g., `deforestation → −3.0`, `net-zero → +2.9`)
- **Multi-page dashboard** — Overview, single-text analyzer, batch analysis with CSV export, and temporal trends
- **Interactive visualizations** — Plotly-powered charts: sentiment gauge, scatter plots, time-series with rolling averages, donut distributions
- **Batch processing** — Analyze up to 18 curated sample articles simultaneously with sidebar filters by category, region, and score range
- **Temporal trends** — Track sentiment evolution over time with annotated climate events and category breakdowns
- **Typed codebase** — Full type hints, dataclasses, and docstrings throughout

---

## Architecture

```
climate-sentiment-analyzer/
├── app.py                        # Overview dashboard (entry point)
├── pages/
│   ├── 1_Analyzer.py             # Single-text analysis with gauge
│   ├── 2_Batch.py                # Multi-article batch + CSV export
│   └── 3_Trends.py               # Temporal trends + rolling average
├── src/
│   └── climate_analyzer/
│       ├── __init__.py
│       ├── analyzer.py           # ClimateAnalyzer NLP engine
│       ├── models.py             # SentimentResult, Article dataclasses
│       └── data.py               # 18-article curated dataset
├── tests/
│   ├── test_analyzer.py          # 25+ unit tests for the NLP engine
│   └── test_models.py            # Data model tests
├── pyproject.toml
└── requirements.txt
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/manpatell/climate-sentiment-analyzer.git
cd climate-sentiment-analyzer

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

---

## Using the Core Library

```python
from src.climate_analyzer import ClimateAnalyzer

analyzer = ClimateAnalyzer()

# Analyze a single text
result = analyzer.analyze(
    "Solar energy hits record efficiency — a clean breakthrough for net-zero goals."
)
print(result.label)      # Positive
print(result.score)      # 0.8225
print(result.climate_keywords)  # ['solar', 'renewable', 'net-zero']

# Batch analysis
texts = {
    "Article A": "Renewable energy transition creates millions of clean jobs.",
    "Article B": "Catastrophic wildfires driven by climate change devastate ecosystems.",
}
results = analyzer.batch_analyze(texts)
for r in results:
    print(f"{r.source_label}: {r.label} ({r.score:+.3f})")

# Top keywords across a corpus
top = analyzer.top_keywords(results, n=10)
```

---

## Sentiment Model

| Score range | Label    | Threshold |
|-------------|----------|-----------|
| ≥ 0.05      | Positive | VADER compound ≥ 0.05 |
| −0.05 – 0.05| Neutral  | −0.05 < compound < 0.05 |
| ≤ −0.05     | Negative | VADER compound ≤ −0.05 |

The model uses VADER's compound score (range −1 to +1), enhanced with a hand-crafted climate domain lexicon that overrides VADER's defaults for terms with strong climate-specific connotation.

---

## Running Tests

```bash
pytest tests/ -v --tb=short
```

With coverage:

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Tech Stack

| Component | Library |
|-----------|---------|
| Dashboard | [Streamlit](https://streamlit.io/) 1.32+ |
| Charts | [Plotly](https://plotly.com/python/) 5.18+ |
| NLP | [VADER Sentiment](https://github.com/cjhutto/vaderSentiment) 3.3+ |
| Data | [Pandas](https://pandas.pydata.org/) 2.0+ |
| Testing | [pytest](https://pytest.org/) 8.0+ |

---

## License

MIT — see [LICENSE](LICENSE).
