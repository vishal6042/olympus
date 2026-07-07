"""Curated few-shot examples for the Few-Shot prompting method.

Hand-written to teach the model two hard skills the problem statement calls out:
  1. Mixed sentiment  — a review can be positive about one thing, negative about another.
  2. Multiple aspects — separate opinions (fit, color, quality, delivery, price ...).

Each example is an (review, product context, ideal JSON analysis) triple. They are
rendered into the few-shot prompt in prompts.py.
"""

FEW_SHOT_EXAMPLES = [
    {
        "review": "The fit is great but the color was not as per the product image.",
        "context": "Department: Dresses | Product: Midi Dress",
        "analysis": {
            "estimated_rating": 3,
            "overall_sentiment": "Neutral",
            "aspects": [
                {"aspect": "fit", "sentiment": "Positive"},
                {"aspect": "color", "sentiment": "Negative"},
            ],
            "urgency": "Medium",
            "reasoning": "",
        },
    },
    {
        "review": "Absolutely love this top! Soft fabric, true to size, and shipped fast.",
        "context": "Department: Tops | Product: Knit Top",
        "analysis": {
            "estimated_rating": 5,
            "overall_sentiment": "Positive",
            "aspects": [
                {"aspect": "fabric", "sentiment": "Positive"},
                {"aspect": "fit", "sentiment": "Positive"},
                {"aspect": "delivery", "sentiment": "Positive"},
            ],
            "urgency": "Low",
            "reasoning": "",
        },
    },
    {
        "review": "Terrible. The dress arrived with a torn seam and the zipper was broken. Very disappointed.",
        "context": "Department: Dresses | Product: Evening Gown",
        "analysis": {
            "estimated_rating": 1,
            "overall_sentiment": "Negative",
            "aspects": [
                {"aspect": "quality", "sentiment": "Negative"},
                {"aspect": "defect", "sentiment": "Negative"},
            ],
            "urgency": "High",
            "reasoning": "",
        },
    },
    {
        "review": "Nice material and the price was reasonable, but it runs a size too small and delivery took two weeks.",
        "context": "Department: Bottoms | Product: Jeans",
        "analysis": {
            "estimated_rating": 3,
            "overall_sentiment": "Neutral",
            "aspects": [
                {"aspect": "material", "sentiment": "Positive"},
                {"aspect": "price", "sentiment": "Positive"},
                {"aspect": "sizing", "sentiment": "Negative"},
                {"aspect": "delivery", "sentiment": "Negative"},
            ],
            "urgency": "Medium",
            "reasoning": "",
        },
    },
    {
        "review": "It's okay. Nothing special but does the job for everyday wear.",
        "context": "Department: Intimate | Product: Camisole",
        "analysis": {
            "estimated_rating": 3,
            "overall_sentiment": "Neutral",
            "aspects": [
                {"aspect": "overall", "sentiment": "Neutral"},
            ],
            "urgency": "Low",
            "reasoning": "",
        },
    },
]
