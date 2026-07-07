"""Objectives 2 & 4 — retail-team reporting.

- generate_retail_report(): OBJECTIVE 4, per review. A short actionable report using the
  estimated rating, sentiment, department and product name as context.
- summarize_by_category_urgency(): OBJECTIVE 2, aggregate. Summarizes a batch of analyzed
  reviews by product category (department) and urgency level. Operates on a DataFrame of
  already-analyzed reviews (see analyze_dataframe) so the dashboard is fast.
"""
import pandas as pd

from config import llm
from schema import ReviewAnalysis
from analyzer import analyze_review, build_context


# ---------------------------------------------------------------- Objective 4 (per review)
def generate_retail_report(analysis: ReviewAnalysis, department: str = "", product: str = "",
                           review: str = "") -> str:
    """Return a short, actionable report for the retail team about one review."""
    aspects = "; ".join(f"{a.aspect}: {a.sentiment}" for a in analysis.aspects) or "n/a"
    context = build_context(department, product) or "n/a"
    system = (
        "You write concise, actionable internal reports for a fashion retail team. "
        "Use 3-4 short bullet points. Be specific and recommend a next action."
    )
    human = (
        f"Product context: {context}\n"
        f"Estimated rating: {analysis.estimated_rating}/5\n"
        f"Overall sentiment: {analysis.overall_sentiment}\n"
        f"Urgency: {analysis.urgency}\n"
        f"Aspect sentiments: {aspects}\n"
        f"Review: \"{review}\"\n\n"
        "Write the retail-team report (include a recommended action)."
    )
    return llm.invoke([("system", system), ("human", human)]).content.strip()


# ---------------------------------------------------------------- Objective 2 (aggregate)
def analyze_dataframe(df: pd.DataFrame, method: str = "cot", limit: int | None = None,
                      progress=None) -> pd.DataFrame:
    """Run the LLM analyzer over a dataframe of reviews and append the results.

    Expects columns: review_text, department_name, class_name. Returns a copy with
    est_rating, pred_sentiment, urgency, aspects, n_aspects added.
    """
    rows = df.head(limit) if limit else df
    est_rating, pred_sentiment, urgency, aspects_txt, n_aspects = [], [], [], [], []
    total = len(rows)
    for i, (_, r) in enumerate(rows.iterrows()):
        ctx = build_context(r.get("department_name", ""), r.get("class_name", ""))
        a = analyze_review(str(r["review_text"]), ctx, method=method)
        est_rating.append(a.estimated_rating)
        pred_sentiment.append(a.overall_sentiment)
        urgency.append(a.urgency)
        aspects_txt.append("; ".join(f"{x.aspect}:{x.sentiment}" for x in a.aspects))
        n_aspects.append(len(a.aspects))
        if progress:
            progress((i + 1) / total)
    out = rows.copy()
    out["est_rating"] = est_rating
    out["pred_sentiment"] = pred_sentiment
    out["urgency"] = urgency
    out["aspects"] = aspects_txt
    out["n_aspects"] = n_aspects
    return out


def summarize_by_category_urgency(analyzed: pd.DataFrame) -> pd.DataFrame:
    """Aggregate analyzed reviews by department x urgency (counts + mean estimated rating)."""
    summary = (
        analyzed.groupby(["department_name", "urgency"])
        .agg(reviews=("est_rating", "size"), avg_est_rating=("est_rating", "mean"))
        .reset_index()
    )
    summary["avg_est_rating"] = summary["avg_est_rating"].round(2)
    return summary


def urgency_pivot(analyzed: pd.DataFrame) -> pd.DataFrame:
    """Department x urgency count matrix (High/Medium/Low columns) for the dashboard."""
    pivot = (
        analyzed.pivot_table(index="department_name", columns="urgency",
                             values="est_rating", aggfunc="size", fill_value=0)
    )
    for col in ["High", "Medium", "Low"]:
        if col not in pivot.columns:
            pivot[col] = 0
    return pivot[["High", "Medium", "Low"]].sort_values("High", ascending=False)
