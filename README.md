# Real-Time Retail Feedback Intelligence — Capstone

A Generative-AI feedback-analysis project for a fashion retail platform (*ChicStyle*). The goal
is to process large volumes of customer reviews, detect sentiment, identify the product/aspect,
flag urgent issues, estimate ratings, and auto-respond to customers.

## Milestone 1 — Data Report & EDA

[`Milestone1_Data_Report.ipynb`](Milestone1_Data_Report.ipynb) covers the full data foundation,
organised into four sections:

1. **Data Description** — shape/size, descriptive statistics, variable types, and inference.
2. **Initial Analysis (EDA)** — univariate, categorical, bivariate analysis and correlations.
3. **Preprocessing** — feature relevance, missing values, outlier treatment, transformations
   and new features (`sentiment`, `review_length`, `log_positive_feedback`, `age_group`).
4. **EDA Conclusion** — key relationships, visual insights, inference, and next steps.

## Data

- `Dataset Real-Time Retail Feedback Intelligence.csv` — raw *Women's E-Commerce Clothing
  Reviews* dataset (semicolon-separated).
- `cleaned_reviews.csv` — cleaned & feature-enriched output of Milestone 1.

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
pip install -r requirements.txt
jupyter notebook Milestone1_Data_Report.ipynb
```
