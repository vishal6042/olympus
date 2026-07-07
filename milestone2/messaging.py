"""Objective 3 — automatically generate a short, personalized customer message.

Based on the review's sentiment: thank positive customers, acknowledge neutral ones, and
apologize to negative ones while telling them a team member will reach out soon.

The message is produced by the LLM (so it reflects the review's specifics), but the
sentiment-based intent and rules are fixed here.
"""
from config import llm
from schema import ReviewAnalysis

# Intent instructions per sentiment, straight from the problem statement.
_INTENT = {
    "Positive": "Warmly THANK the customer for their positive feedback. Keep it upbeat.",
    "Neutral": "ACKNOWLEDGE the customer's feedback and thank them for sharing it.",
    "Negative": (
        "Sincerely APOLOGIZE for the poor experience and clearly reassure the customer that a "
        "team member will reach out to them soon to resolve it."
    ),
}


def generate_customer_message(analysis: ReviewAnalysis, review: str = "") -> str:
    """Return a short (2-3 sentence) personalized message for the customer."""
    intent = _INTENT[analysis.overall_sentiment]
    aspects = ", ".join(a.aspect for a in analysis.aspects) or "their experience"
    system = (
        "You write short, warm, professional customer-service messages for ChicStyle, a fashion "
        "retailer. Write 2-3 sentences, first person from the brand, no subject line, no placeholders."
    )
    human = (
        f"Customer sentiment: {analysis.overall_sentiment}. "
        f"Aspects they mentioned: {aspects}. "
        f"Their review: \"{review}\"\n\n"
        f"Instruction: {intent}"
    )
    return llm.invoke([("system", system), ("human", human)]).content.strip()
