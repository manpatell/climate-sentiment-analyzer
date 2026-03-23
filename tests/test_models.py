"""Unit tests for SentimentResult and Article data models."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.climate_analyzer.models import Article, SentimentResult


def make_result(**kwargs) -> SentimentResult:
    defaults = dict(
        text="Sample climate text.",
        score=0.5,
        label="Positive",
        confidence=0.8,
        positive_score=0.4,
        negative_score=0.1,
        neutral_score=0.5,
        climate_keywords=["solar", "renewable"],
        keyword_density=0.15,
        word_count=30,
    )
    defaults.update(kwargs)
    return SentimentResult(**defaults)


# ── SentimentResult ───────────────────────────────────────────────────────────

class TestSentimentResult:
    def test_sentiment_color_positive(self):
        r = make_result(label="Positive")
        assert r.sentiment_color == "#2ECC71"

    def test_sentiment_color_negative(self):
        r = make_result(label="Negative")
        assert r.sentiment_color == "#E74C3C"

    def test_sentiment_color_neutral(self):
        r = make_result(label="Neutral")
        assert r.sentiment_color == "#F39C12"

    def test_sentiment_emoji_positive(self):
        r = make_result(label="Positive")
        assert r.sentiment_emoji == "🟢"

    def test_sentiment_emoji_negative(self):
        r = make_result(label="Negative")
        assert r.sentiment_emoji == "🔴"

    def test_sentiment_emoji_neutral(self):
        r = make_result(label="Neutral")
        assert r.sentiment_emoji == "🟡"

    def test_to_dict_contains_expected_keys(self):
        r = make_result(source_label="Test Article")
        d = r.to_dict()
        expected_keys = {
            "source", "score", "label", "confidence",
            "positive", "negative", "neutral",
            "keyword_density", "word_count", "climate_keywords", "analyzed_at",
        }
        assert expected_keys.issubset(d.keys())

    def test_to_dict_source_uses_source_label(self):
        r = make_result(source_label="My Article")
        assert r.to_dict()["source"] == "My Article"

    def test_to_dict_source_defaults_to_custom(self):
        r = make_result(source_label=None)
        assert r.to_dict()["source"] == "custom"

    def test_to_dict_keywords_joined(self):
        r = make_result(climate_keywords=["solar", "wind", "climate"])
        d = r.to_dict()
        assert d["climate_keywords"] == "solar, wind, climate"

    def test_analyzed_at_defaults_to_now(self):
        before = datetime.utcnow()
        r = make_result()
        after = datetime.utcnow()
        assert before <= r.analyzed_at <= after

    def test_optional_source_label_defaults_none(self):
        r = make_result()
        assert r.source_label is None


# ── Article ───────────────────────────────────────────────────────────────────

class TestArticle:
    def _make_article(self, title: str = "A" * 50) -> Article:
        return Article(
            id="test-01",
            title=title,
            body="Sample body text.",
            source="Test Source",
            category="Technology",
            published_at=datetime(2025, 9, 1),
            region="Global",
        )

    def test_short_title_truncates_long_titles(self):
        a = self._make_article("A" * 50)
        assert len(a.short_title) <= 40
        assert a.short_title.endswith("…")

    def test_short_title_keeps_short_titles_unchanged(self):
        title = "Solar breakthrough"
        a = self._make_article(title)
        assert a.short_title == title

    def test_short_title_exactly_40_chars_unchanged(self):
        title = "X" * 40
        a = self._make_article(title)
        assert a.short_title == title

    def test_region_defaults_to_global(self):
        a = Article(
            id="x",
            title="T",
            body="B",
            source="S",
            category="Policy",
            published_at=datetime.utcnow(),
        )
        assert a.region == "Global"
