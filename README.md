# Real-Time Retail Feedback Intelligence — Capstone

A Generative-AI feedback-analysis system for **ChicStyle**, a fashion retail platform. During
festive sales the platform is flooded with customer reviews; slow responses to negative or urgent
feedback erode trust and revenue. This project turns that unstructured feedback into real-time,
actionable business intelligence.

**The system's four objectives:**
1. Analyze reviews and **estimate the product rating** in real time.
2. **Summarize insights** by product category and urgency level.
3. Auto-generate **personalized customer messages** by sentiment (thank / acknowledge / apologize).
4. Generate short, **actionable retail-team reports** (rating + sentiment + department + product).

---

## Milestone 1 — Data Report & EDA

[`Milestone1_Data_Report.ipynb`](Milestone1_Data_Report.ipynb) builds the data foundation in four
sections:

1. **Data Description** — shape/size, descriptive statistics, variable types, inference.
2. **Initial Analysis (EDA)** — univariate, categorical, bivariate analysis and correlations.
3. **Preprocessing** — feature relevance, missing values, outlier treatment, and new features
   (`sentiment`, `review_length`, `log_positive_feedback`, `age_group`).
4. **EDA Conclusion** — key relationships, visual insights, and next steps.

**Data**
- `Dataset Real-Time Retail Feedback Intelligence.csv` — raw *Women's E-Commerce Clothing Reviews*
  (semicolon-separated).
- `cleaned_reviews.csv` — cleaned & feature-enriched output of Milestone 1.

---

## Milestone 2 — GenAI Prompt Engineering & Streamlit

A modular system ([`milestone2/`](milestone2)) powered by **Azure OpenAI** that analyzes a review
with three prompting techniques — **Zero-Shot**, **Few-Shot**, and **Chain-of-Thought** — and
returns an estimated rating, overall + per-aspect sentiment, and urgency, then produces a
personalized customer message and a retail-team report.

- **Experiments & method comparison:** [`Milestone2_Prompt_Engineering.ipynb`](Milestone2_Prompt_Engineering.ipynb)
  runs the three methods on a balanced ~50-review sample, scores them against the Milestone-1
  ground truth, and precomputes `analyzed_reviews.csv` for the dashboard.
- **Final product:** a professional **Streamlit** app — see [`milestone2/README.md`](milestone2/README.md).

---

## Repository structure

```
capstone_project/
├── Dataset Real-Time Retail Feedback Intelligence.csv   # raw dataset
├── cleaned_reviews.csv                                  # M1 cleaned/enriched output
├── analyzed_reviews.csv                                 # M2 GenAI-analyzed sample (dashboard)
├── Milestone1_Data_Report.ipynb                         # M1: data report & EDA
├── Milestone2_Prompt_Engineering.ipynb                  # M2: prompting experiments & comparison
├── requirements.txt                                     # M1 dependencies
└── milestone2/                                          # M2 modular GenAI app
    ├── app.py            # Streamlit UI (sidebar nav: Analyze / Batch Insights / Comparison)
    ├── config.py         # Azure OpenAI client from .env
    ├── schema.py         # ReviewAnalysis output schema (pydantic)
    ├── prompts.py        # Zero-Shot / Few-Shot / CoT prompt builders
    ├── examples.py       # curated few-shot examples (mixed sentiment, multi-aspect)
    ├── analyzer.py       # analyze_review() — prompt → LLM → structured result
    ├── messaging.py      # personalized customer message (Objective 3)
    ├── reports.py        # retail report + category/urgency summary (Objectives 4 & 2)
    ├── requirements.txt  # M2 dependencies
    └── .env.example      # Azure config template (copy to .env, add your key)
```

---

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate                       # Windows (use source .venv/bin/activate on macOS/Linux)

# Milestone 1
pip install -r requirements.txt

# Milestone 2 (Azure OpenAI + Streamlit)
pip install -r milestone2/requirements.txt
cp milestone2/.env.example milestone2/.env   # then paste your AZURE_OPENAI_API_KEY
```

## Running

```bash
# Milestone 1 / 2 notebooks
jupyter notebook Milestone1_Data_Report.ipynb
jupyter notebook Milestone2_Prompt_Engineering.ipynb

# Milestone 2 app
cd milestone2 && streamlit run app.py
```

## Security

The Azure key is read only from `milestone2/.env`, which is **gitignored** and must never be
committed. Use `milestone2/.env.example` (blank key) as the shareable template.

## Tech stack

- **Milestone 1:** Python, pandas, numpy, matplotlib, seaborn.
- **Milestone 2:** Azure OpenAI, LangChain (`langchain-openai`), pydantic, Streamlit.
