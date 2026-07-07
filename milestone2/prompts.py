"""Prompt templates for the three prompting methods: Zero-Shot, Few-Shot, Chain-of-Thought.

Each builds a list of chat messages (system + user) for the LLM. The model is bound to the
`ReviewAnalysis` schema in analyzer.py, so these prompts describe *what* to extract, not the
JSON formatting itself.
"""
import json
from examples import FEW_SHOT_EXAMPLES

# Shared role / task description used by every method.
SYSTEM_ROLE = (
    "You are a retail feedback-analysis assistant for ChicStyle, an online fashion retailer. "
    "You read a single customer review and analyze it for the retail team. "
    "Detect the overall sentiment (Positive, Negative, or Neutral), break the review into the "
    "specific aspects it discusses (e.g. fit, color, quality, delivery, price, sizing) and assign "
    "a sentiment to each aspect, estimate the product rating from 1 (worst) to 5 (best), and judge "
    "how urgently the team should respond (High for serious complaints such as defects, wrong or "
    "damaged items, or angry customers; Low for simple praise)."
)


def _context_block(context: str) -> str:
    return f"\nProduct context: {context}" if context else ""


def zero_shot_messages(review: str, context: str = ""):
    """Zero-Shot: instruction only, no examples."""
    system = SYSTEM_ROLE
    user = f"Analyze the following customer review.{_context_block(context)}\n\nReview: \"{review}\""
    return [("system", system), ("human", user)]


def few_shot_messages(review: str, context: str = ""):
    """Few-Shot: prepend curated examples that demonstrate mixed sentiment & multiple aspects."""
    lines = [
        SYSTEM_ROLE,
        "\nHere are examples of correctly analyzed reviews. Note how a single review can be "
        "positive about one aspect and negative about another (mixed sentiment):",
    ]
    for ex in FEW_SHOT_EXAMPLES:
        lines.append(f"\nReview: \"{ex['review']}\"")
        if ex["context"]:
            lines.append(f"Product context: {ex['context']}")
        lines.append("Analysis: " + json.dumps(ex["analysis"]))
    system = "\n".join(lines)
    user = f"Now analyze this new review the same way.{_context_block(context)}\n\nReview: \"{review}\""
    return [("system", system), ("human", user)]


def cot_messages(review: str, context: str = ""):
    """Chain-of-Thought: guide the model through explicit reasoning steps."""
    system = (
        SYSTEM_ROLE
        + "\n\nThink step by step and record your reasoning in the `reasoning` field:\n"
        "Step 1: Identify every distinct aspect the review mentions.\n"
        "Step 2: Assign a sentiment (Positive/Negative/Neutral) to each aspect.\n"
        "Step 3: Weigh the aspects to decide the overall sentiment and estimate the 1-5 rating.\n"
        "Step 4: Decide the urgency based on how serious the negative aspects are.\n"
        "Put your step-by-step explanation in `reasoning`, then fill the other fields accordingly."
    )
    user = f"Analyze the following customer review, reasoning step by step.{_context_block(context)}\n\nReview: \"{review}\""
    return [("system", system), ("human", user)]


# Registry so callers can select a method by name.
PROMPT_BUILDERS = {
    "zero_shot": zero_shot_messages,
    "few_shot": few_shot_messages,
    "cot": cot_messages,
}

METHOD_LABELS = {
    "zero_shot": "Zero-Shot",
    "few_shot": "Few-Shot",
    "cot": "Chain-of-Thought",
}
