"""ChicStyle — Real-Time Retail Feedback Intelligence (Streamlit app).

Final Milestone-2 product. Three tabs:
  1. Analyze a Review   — single review -> rating, sentiment, aspects, urgency, message, report.
  2. Batch Insights     — category x urgency dashboard over the analyzed dataset (Objective 2 & 4).
  3. Method Comparison  — Zero-Shot vs Few-Shot vs Chain-of-Thought side by side.
"""
import os
import pandas as pd
import streamlit as st

from analyzer import analyze_review, build_context
from messaging import generate_customer_message
from reports import (generate_retail_report, analyze_dataframe,
                     summarize_by_category_urgency, urgency_pivot)
from prompts import METHOD_LABELS

st.set_page_config(page_title="ChicStyle Feedback Intelligence", page_icon="🛍️", layout="wide")

DEPARTMENTS = ["", "Tops", "Dresses", "Bottoms", "Intimate", "Jackets", "Trend"]
METHOD_KEYS = {v: k for k, v in METHOD_LABELS.items()}   # label -> key
_SENT_COLOR = {"Positive": "#5cb85c", "Neutral": "#f0ad4e", "Negative": "#d9534f"}
_URG_COLOR = {"High": "#d9534f", "Medium": "#f0ad4e", "Low": "#5cb85c"}


def badge(text: str, color: str) -> str:
    return (f"<span style='display:inline-block;padding:4px 12px;border-radius:20px;"
            f"background:{color};color:white;font-size:13px;font-weight:600;'>{text}</span>")


def stars(n: int) -> str:
    return "⭐" * int(n) + "☆" * (5 - int(n))


# ----------------------------------------------------------------- Sidebar
with st.sidebar:
    st.header("🛍️ ChicStyle")
    st.caption("Real-Time Retail Feedback Intelligence")
    st.divider()
    page = st.radio("Navigate", ["🔍 Analyze a Review", "📊 Batch Insights", "🧪 Method Comparison"])
    st.divider()
    method_label = st.radio("Prompting method", list(METHOD_LABELS.values()), index=2,
                            help="Zero-Shot, Few-Shot, or Chain-of-Thought reasoning.")
    method = METHOD_KEYS[method_label]
    st.divider()
    st.subheader("⚡ Capabilities")
    st.markdown(
        "- Estimate product rating\n"
        "- Detect sentiment & aspects\n"
        "- Flag urgent issues\n"
        "- Auto customer messages\n"
        "- Category & urgency insights"
    )
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        st.warning("Add your key to `milestone2/.env` (AZURE_OPENAI_API_KEY).")

st.title("🛍️ ChicStyle Feedback Intelligence")
st.markdown("AI-powered analysis of customer reviews using **Azure OpenAI** prompt engineering.")

# ----------------------------------------------------------------- Page 1: single review
if page == "🔍 Analyze a Review":
    col1, col2 = st.columns([3, 2])
    with col1:
        review = st.text_area("Customer review", height=140,
                              placeholder="e.g. The fit is great but the color was not as per the image.")
    with col2:
        department = st.selectbox("Department (optional)", DEPARTMENTS)
        product = st.text_input("Product name (optional)", placeholder="e.g. Midi Dress")

    if st.button("Analyze review", type="primary"):
        if not review.strip():
            st.error("Please enter a review.")
        else:
            context = build_context(department, product)
            with st.spinner(f"Analyzing with {method_label}…"):
                analysis = analyze_review(review, context, method=method)
                message = generate_customer_message(analysis, review)
                report = generate_retail_report(analysis, department, product, review)

            m1, m2, m3 = st.columns(3)
            m1.markdown(f"**Estimated rating**\n\n{stars(analysis.estimated_rating)} "
                        f"({analysis.estimated_rating}/5)")
            m2.markdown("**Sentiment**\n\n" +
                        badge(analysis.overall_sentiment, _SENT_COLOR[analysis.overall_sentiment]),
                        unsafe_allow_html=True)
            m3.markdown("**Urgency**\n\n" +
                        badge(analysis.urgency, _URG_COLOR[analysis.urgency]),
                        unsafe_allow_html=True)

            st.subheader("Aspects")
            if analysis.aspects:
                st.dataframe(pd.DataFrame([{"Aspect": a.aspect, "Sentiment": a.sentiment}
                                           for a in analysis.aspects]),
                             hide_index=True, use_container_width=True)
            else:
                st.caption("No specific aspects detected.")

            if analysis.reasoning:
                with st.expander("🧠 Chain-of-Thought reasoning"):
                    st.write(analysis.reasoning)

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("💬 Customer message")
                st.info(message)
            with c2:
                st.subheader("📋 Retail-team report")
                st.markdown(report)


# ----------------------------------------------------------------- Page 2: batch insights
elif page == "📊 Batch Insights":
    st.markdown("Summarize insights **by product category and urgency level** across many reviews "
                "(Objective 2). Uses precomputed GenAI analysis for speed.")

    @st.cache_data
    def load_analyzed():
        for path in ("analyzed_reviews.csv", "../analyzed_reviews.csv"):
            if os.path.exists(path):
                return pd.read_csv(path)
        return None

    analyzed = load_analyzed()
    uploaded = st.file_uploader("…or upload reviews CSV to analyze live (review_text, department_name)",
                                type=["csv"])
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        n = st.slider("Reviews to analyze", 5, min(100, len(raw)), min(30, len(raw)))
        if st.button("Analyze uploaded reviews", type="primary"):
            bar = st.progress(0.0)
            analyzed = analyze_dataframe(raw.head(n), method=method, progress=bar.progress)
            bar.empty()

    if analyzed is None:
        st.info("No `analyzed_reviews.csv` found yet. Run the Milestone-2 notebook to generate it, "
                "or upload a CSV above.")
    else:
        total = len(analyzed)
        high = int((analyzed["urgency"] == "High").sum())
        k1, k2, k3 = st.columns(3)
        k1.metric("Reviews analyzed", f"{total:,}")
        k2.metric("High-urgency", f"{high:,}", f"{high/total*100:.0f}%")
        k3.metric("Avg est. rating", f"{analyzed['est_rating'].mean():.2f} / 5")

        st.subheader("Department × Urgency")
        pivot = urgency_pivot(analyzed)
        st.bar_chart(pivot)
        st.dataframe(pivot, use_container_width=True)

        st.subheader("Summary table")
        summary = summarize_by_category_urgency(analyzed)
        st.dataframe(summary, hide_index=True, use_container_width=True)
        st.download_button("⬇️ Download summary (CSV)", summary.to_csv(index=False),
                           "category_urgency_summary.csv", "text/csv")


# ----------------------------------------------------------------- Page 3: method comparison
elif page == "🧪 Method Comparison":
    st.markdown("Compare **Zero-Shot vs Few-Shot vs Chain-of-Thought** on the same review.")
    cmp_review = st.text_area("Review to compare", height=110,
                              placeholder="e.g. Nice material and fair price, but runs small and shipped late.",
                              key="cmp_review")
    cmp_dept = st.selectbox("Department (optional)", DEPARTMENTS, key="cmp_dept")
    if st.button("Run all three methods", type="primary"):
        if not cmp_review.strip():
            st.error("Please enter a review.")
        else:
            ctx = build_context(cmp_dept, "")
            cols = st.columns(3)
            for col, key in zip(cols, ["zero_shot", "few_shot", "cot"]):
                with col:
                    st.markdown(f"#### {METHOD_LABELS[key]}")
                    with st.spinner("…"):
                        a = analyze_review(cmp_review, ctx, method=key)
                    st.markdown(f"{stars(a.estimated_rating)} ({a.estimated_rating}/5)")
                    st.markdown(badge(a.overall_sentiment, _SENT_COLOR[a.overall_sentiment]) + " " +
                                badge(a.urgency, _URG_COLOR[a.urgency]), unsafe_allow_html=True)
                    st.caption(f"{len(a.aspects)} aspect(s)")
                    for asp in a.aspects:
                        st.write(f"- {asp.aspect}: {asp.sentiment}")
