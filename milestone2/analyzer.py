"""Core review-analysis orchestration.

Ties together the chosen prompt method + the Azure LLM + the structured schema, returning a
typed `ReviewAnalysis` for a single review. This is the one function shared by both the
notebook experiments and the Streamlit app.
"""
from config import llm
from schema import ReviewAnalysis
from prompts import PROMPT_BUILDERS

# Bind the LLM to the schema once so every call returns a parsed ReviewAnalysis.
_structured_llm = llm.with_structured_output(ReviewAnalysis)


def analyze_review(review: str, context: str = "", method: str = "cot") -> ReviewAnalysis:
    """Analyze one review with the given prompting method.

    Args:
        review: raw customer review text.
        context: optional product context string, e.g. "Department: Dresses | Product: Midi Dress".
        method: one of "zero_shot", "few_shot", "cot".
    Returns:
        ReviewAnalysis with estimated_rating, overall_sentiment, aspects, urgency, reasoning.
    """
    if method not in PROMPT_BUILDERS:
        raise ValueError(f"Unknown method '{method}'. Choose from {list(PROMPT_BUILDERS)}.")
    messages = PROMPT_BUILDERS[method](review, context)
    return _structured_llm.invoke(messages)


def build_context(department: str = "", product: str = "") -> str:
    """Helper to format product context consistently from separate fields."""
    parts = []
    if department:
        parts.append(f"Department: {department}")
    if product:
        parts.append(f"Product: {product}")
    return " | ".join(parts)
