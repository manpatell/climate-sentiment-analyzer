"""Climate Sentiment Analyzer — NLP pipeline for climate & sustainability news."""

from .analyzer import ClimateAnalyzer
from .models import SentimentResult, Article

__all__ = ["ClimateAnalyzer", "SentimentResult", "Article"]
__version__ = "1.0.0"
