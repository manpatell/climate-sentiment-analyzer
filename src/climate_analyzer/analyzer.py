"""Core NLP engine for climate-focused sentiment analysis.

Wraps VADER (Valence Aware Dictionary and sEntiment Reasoner) and extends it
with a domain-specific climate lexicon so that terms like 'emissions' and
'deforestation' carry appropriate negative weight, while 'renewable' and
'net-zero' carry appropriate positive weight.
"""

from __future__ import annotations

import logging
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

# Allow running as a script without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .models import Article, SentimentResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Climate-specific lexicon extensions
# ---------------------------------------------------------------------------

_CLIMATE_POSITIVE: dict[str, float] = {
    "renewable": 2.8,
    "sustainable": 2.5,
    "clean": 2.2,
    "breakthrough": 3.0,
    "innovative": 2.4,
    "transition": 1.8,
    "decarbonize": 2.6,
    "electrify": 2.3,
    "reforestation": 2.7,
    "conservation": 2.5,
    "resilient": 2.2,
    "net-zero": 2.9,
    "carbon-neutral": 2.9,
    "biodegradable": 2.0,
    "circular": 2.1,
    "efficiency": 2.0,
    "mitigation": 1.9,
    "adaptation": 1.8,
    "restoration": 2.4,
    "progress": 2.0,
}

_CLIMATE_NEGATIVE: dict[str, float] = {
    "emissions": -2.0,
    "pollution": -2.8,
    "warming": -2.5,
    "flooding": -2.7,
    "drought": -2.6,
    "wildfire": -2.8,
    "deforestation": -3.0,
    "extinction": -3.0,
    "catastrophic": -3.2,
    "irreversible": -2.9,
    "methane": -1.8,
    "smog": -2.4,
    "toxic": -2.8,
    "contamination": -2.6,
    "bleaching": -2.5,
    "acidification": -2.7,
    "permafrost": -1.5,
    "tipping": -2.2,
    "displacement": -2.4,
    "collapse": -3.1,
}

# Keywords used to compute "climate relevance" of a text
_CLIMATE_KEYWORDS: frozenset[str] = frozenset(
    {
        "carbon", "co2", "emissions", "temperature", "fossil", "renewable",
        "solar", "wind", "electric", "climate", "greenhouse", "deforestation",
        "biodiversity", "ocean", "arctic", "glacier", "methane", "ozone",
        "atmosphere", "ecology", "sustainability", "drought", "wildfire",
        "flooding", "coral", "permafrost", "biomass", "geothermal",
        "hydropower", "nuclear", "electrification", "net-zero", "reforestation",
        "carbon-capture", "sea-level", "pollution", "habitat", "ecosystem",
        "conservation", "extinction", "warming", "acidification",
    }
)


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

class ClimateAnalyzer:
    """NLP pipeline for climate-focused sentiment analysis.

    Usage::

        analyzer = ClimateAnalyzer()
        result = analyzer.analyze("Solar energy hits record efficiency levels.")
        print(result.label, result.score)
    """

    def __init__(self) -> None:
        self._vader = SentimentIntensityAnalyzer()
        # Inject climate-domain overrides into VADER's internal lexicon
        self._vader.lexicon.update(_CLIMATE_POSITIVE)
        self._vader.lexicon.update(_CLIMATE_NEGATIVE)
        logger.info(
            "ClimateAnalyzer ready (+%d positive, +%d negative custom terms)",
            len(_CLIMATE_POSITIVE),
            len(_CLIMATE_NEGATIVE),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Lowercase word tokenization preserving hyphenated terms."""
        return re.findall(r"\b[a-z][a-z\-]*[a-z]\b|\b[a-z]\b", text.lower())

    @staticmethod
    def _extract_keywords(tokens: list[str]) -> list[str]:
        return [t for t in tokens if t in _CLIMATE_KEYWORDS]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, text: str, source_label: Optional[str] = None) -> SentimentResult:
        """Run the full NLP pipeline on a single text string.

        Args:
            text: Raw input text (news article, report, tweet, etc.).
            source_label: Optional display name for the result (e.g. article title).

        Returns:
            A :class:`SentimentResult` with scores, label, and keyword metadata.

        Raises:
            ValueError: If *text* is empty or whitespace-only.
        """
        if not text or not text.strip():
            raise ValueError("Input text must not be empty.")

        scores = self._vader.polarity_scores(text)
        tokens = self._tokenize(text)
        keywords = self._extract_keywords(tokens)
        compound = scores["compound"]

        if compound >= 0.05:
            label = "Positive"
        elif compound <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"

        # Confidence: how far the compound score departs from the neutral band
        confidence = round(min(abs(compound) / 0.95, 1.0), 4)

        return SentimentResult(
            text=text,
            score=round(compound, 4),
            label=label,
            confidence=confidence,
            positive_score=round(scores["pos"], 4),
            negative_score=round(scores["neg"], 4),
            neutral_score=round(scores["neu"], 4),
            climate_keywords=keywords,
            keyword_density=round(len(keywords) / max(len(tokens), 1), 4),
            word_count=len(tokens),
            source_label=source_label,
        )

    def analyze_article(self, article: Article) -> SentimentResult:
        """Convenience wrapper that analyzes an :class:`Article` object."""
        result = self.analyze(article.body, source_label=article.title)
        result.analyzed_at = article.published_at
        return result

    def batch_analyze(
        self,
        texts: dict[str, str],
        sort_by: str = "score",
    ) -> list[SentimentResult]:
        """Analyze multiple labeled texts.

        Args:
            texts: Mapping of {display_label: text_content}.
            sort_by: Sort results by "score" (descending) or "label".

        Returns:
            List of :class:`SentimentResult`, sorted per *sort_by*.
        """
        results: list[SentimentResult] = []
        for label, text in texts.items():
            try:
                results.append(self.analyze(text, source_label=label))
            except ValueError:
                logger.warning("Skipping empty text for label '%s'", label)

        if sort_by == "score":
            results.sort(key=lambda r: r.score, reverse=True)
        elif sort_by == "label":
            results.sort(key=lambda r: r.label)

        return results

    def top_keywords(
        self,
        results: list[SentimentResult],
        n: int = 20,
    ) -> list[tuple[str, int]]:
        """Aggregate and rank climate keyword frequencies across multiple results.

        Args:
            results: Output from :meth:`batch_analyze` or a list of individual results.
            n: Maximum number of keywords to return.

        Returns:
            List of (keyword, count) tuples, sorted by count descending.
        """
        counter: Counter[str] = Counter()
        for r in results:
            counter.update(r.climate_keywords)
        return counter.most_common(n)
