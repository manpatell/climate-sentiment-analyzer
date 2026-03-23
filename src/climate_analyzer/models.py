"""Data models for the Climate Sentiment Analyzer."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SentimentResult:
    """Encapsulates the full output of a single sentiment analysis."""

    text: str
    score: float          # Compound score: -1.0 (most negative) to 1.0 (most positive)
    label: str            # "Positive" | "Negative" | "Neutral"
    confidence: float     # 0.0 to 1.0 — distance from neutral threshold
    positive_score: float
    negative_score: float
    neutral_score: float
    climate_keywords: list[str]
    keyword_density: float   # climate keywords / total word count
    word_count: int
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
    source_label: Optional[str] = None

    @property
    def sentiment_color(self) -> str:
        """Hex color mapped to sentiment label."""
        if self.label == "Positive":
            return "#2ECC71"
        if self.label == "Negative":
            return "#E74C3C"
        return "#F39C12"

    @property
    def sentiment_emoji(self) -> str:
        if self.label == "Positive":
            return "🟢"
        if self.label == "Negative":
            return "🔴"
        return "🟡"

    def to_dict(self) -> dict:
        """Serialize to a flat dict suitable for DataFrame construction."""
        return {
            "source": self.source_label or "custom",
            "score": self.score,
            "label": self.label,
            "confidence": self.confidence,
            "positive": self.positive_score,
            "negative": self.negative_score,
            "neutral": self.neutral_score,
            "keyword_density": self.keyword_density,
            "word_count": self.word_count,
            "climate_keywords": ", ".join(self.climate_keywords),
            "analyzed_at": self.analyzed_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


@dataclass
class Article:
    """A curated climate news article used in sample datasets."""

    id: str
    title: str
    body: str
    source: str
    category: str       # "Technology" | "Policy" | "Science" | "Impact"
    published_at: datetime
    region: str = "Global"

    @property
    def short_title(self) -> str:
        """Truncated title for chart labels."""
        return self.title if len(self.title) <= 40 else self.title[:37] + "…"
