"""Structured output schema for a single review analysis.

The LLM is bound to this pydantic model via `llm.with_structured_output(ReviewAnalysis)`,
guaranteeing a parseable, typed result instead of free-form text.
"""
from typing import List, Literal
from pydantic import BaseModel, Field

Sentiment = Literal["Positive", "Negative", "Neutral"]
Urgency = Literal["High", "Medium", "Low"]


class AspectSentiment(BaseModel):
    """Sentiment about one specific aspect mentioned in the review."""
    aspect: str = Field(description="The specific aspect discussed, e.g. fit, color, quality, delivery, price.")
    sentiment: Sentiment = Field(description="Sentiment expressed about this aspect.")


class ReviewAnalysis(BaseModel):
    """Full structured analysis of a single customer review."""
    estimated_rating: int = Field(ge=1, le=5, description="Estimated product rating from 1 (worst) to 5 (best).")
    overall_sentiment: Sentiment = Field(description="Overall sentiment of the review.")
    aspects: List[AspectSentiment] = Field(
        default_factory=list,
        description="List of aspects mentioned, each with its own sentiment (captures mixed sentiment).",
    )
    urgency: Urgency = Field(description="How urgently the retail team should respond (High for serious complaints).")
    reasoning: str = Field(
        default="",
        description="Step-by-step reasoning. Populated only by the Chain-of-Thought method; empty otherwise.",
    )
