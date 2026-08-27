"""Recommendation engine module."""

from .recommender import recommend_resources
from .ranker import ResourceRanker
from .explain import ExplanationGenerator

__all__ = [
    "recommend_resources",
    "ResourceRanker",
    "ExplanationGenerator",
]
