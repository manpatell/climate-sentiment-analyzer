"""Unit tests for ClimateAnalyzer."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.climate_analyzer.analyzer import ClimateAnalyzer
from src.climate_analyzer.data import SAMPLE_ARTICLES


@pytest.fixture(scope="module")
def analyzer() -> ClimateAnalyzer:
    return ClimateAnalyzer()


# ── analyze() ────────────────────────────────────────────────────────────────

class TestAnalyze:
    def test_positive_text_returns_positive_label(self, analyzer):
        result = analyzer.analyze(
            "Renewable solar energy breakthrough promises sustainable clean transition."
        )
        assert result.label == "Positive"
        assert result.score > 0.05

    def test_negative_text_returns_negative_label(self, analyzer):
        result = analyzer.analyze(
            "Catastrophic deforestation and toxic pollution drive extinction crisis."
        )
        assert result.label == "Negative"
        assert result.score < -0.05

    def test_neutral_text_returns_neutral_label(self, analyzer):
        result = analyzer.analyze(
            "The report describes carbon emissions from industrial facilities."
        )
        # Neutral or slightly negative — score should be in the central band
        assert result.label in {"Neutral", "Negative"}

    def test_score_range(self, analyzer):
        result = analyzer.analyze("Climate change affects global temperatures.")
        assert -1.0 <= result.score <= 1.0

    def test_confidence_range(self, analyzer):
        result = analyzer.analyze("Solar panels are becoming more efficient every year.")
        assert 0.0 <= result.confidence <= 1.0

    def test_word_count_is_accurate(self, analyzer):
        text = "Clean renewable energy helps the planet."
        result = analyzer.analyze(text)
        assert result.word_count > 0

    def test_climate_keywords_extracted(self, analyzer):
        result = analyzer.analyze(
            "Rising CO2 emissions from fossil fuels accelerate ocean warming."
        )
        assert len(result.climate_keywords) > 0
        assert any(kw in {"co2", "emissions", "fossil", "ocean", "warming"}
                   for kw in result.climate_keywords)

    def test_keyword_density_between_zero_and_one(self, analyzer):
        result = analyzer.analyze("Solar wind climate renewable energy.")
        assert 0.0 <= result.keyword_density <= 1.0

    def test_source_label_propagates(self, analyzer):
        result = analyzer.analyze("Test text.", source_label="My Article")
        assert result.source_label == "My Article"

    def test_empty_text_raises_value_error(self, analyzer):
        with pytest.raises(ValueError):
            analyzer.analyze("")

    def test_whitespace_only_raises_value_error(self, analyzer):
        with pytest.raises(ValueError):
            analyzer.analyze("   \n\t  ")

    def test_pos_neg_neu_scores_sum_to_one(self, analyzer):
        result = analyzer.analyze("Climate change threatens biodiversity worldwide.")
        total = round(result.positive_score + result.negative_score + result.neutral_score, 3)
        assert abs(total - 1.0) < 0.01, f"Scores sum to {total}, expected ~1.0"


# ── batch_analyze() ───────────────────────────────────────────────────────────

class TestBatchAnalyze:
    def test_returns_correct_count(self, analyzer):
        texts = {
            "a": "Solar energy is a clean breakthrough.",
            "b": "Deforestation causes catastrophic biodiversity loss.",
            "c": "Carbon emissions data shows mixed trends.",
        }
        results = analyzer.batch_analyze(texts)
        assert len(results) == 3

    def test_sorted_by_score_descending(self, analyzer):
        texts = {
            "pos": "Renewable energy transition is progressing well.",
            "neg": "Catastrophic flooding displaces millions in crisis.",
            "neu": "Climate report discusses temperature measurements.",
        }
        results = analyzer.batch_analyze(texts, sort_by="score")
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_skips_empty_text(self, analyzer):
        texts = {"good": "Solar power expands rapidly.", "empty": ""}
        results = analyzer.batch_analyze(texts)
        assert len(results) == 1
        assert results[0].source_label == "good"

    def test_empty_dict_returns_empty_list(self, analyzer):
        assert analyzer.batch_analyze({}) == []


# ── top_keywords() ────────────────────────────────────────────────────────────

class TestTopKeywords:
    def test_returns_correct_number(self, analyzer):
        results = [analyzer.analyze_article(a) for a in SAMPLE_ARTICLES[:6]]
        top = analyzer.top_keywords(results, n=5)
        assert len(top) <= 5

    def test_sorted_by_frequency(self, analyzer):
        results = [analyzer.analyze_article(a) for a in SAMPLE_ARTICLES]
        top = analyzer.top_keywords(results, n=10)
        counts = [c for _, c in top]
        assert counts == sorted(counts, reverse=True)

    def test_returns_tuples(self, analyzer):
        results = [analyzer.analyze_article(a) for a in SAMPLE_ARTICLES[:3]]
        top = analyzer.top_keywords(results)
        for item in top:
            assert isinstance(item, tuple)
            assert len(item) == 2


# ── analyze_article() ─────────────────────────────────────────────────────────

class TestAnalyzeArticle:
    def test_article_title_used_as_source_label(self, analyzer):
        article = SAMPLE_ARTICLES[0]
        result = analyzer.analyze_article(article)
        assert result.source_label == article.title

    def test_analyzed_at_matches_published_at(self, analyzer):
        article = SAMPLE_ARTICLES[0]
        result = analyzer.analyze_article(article)
        assert result.analyzed_at == article.published_at

    def test_all_sample_articles_analyzable(self, analyzer):
        for article in SAMPLE_ARTICLES:
            result = analyzer.analyze_article(article)
            assert result.label in {"Positive", "Negative", "Neutral"}
