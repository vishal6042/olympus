# Milestone 2 — ChicStyle Feedback Intelligence (GenAI)

Real-time retail feedback system built with **Azure OpenAI** prompt engineering
(Zero-Shot, Few-Shot, Chain-of-Thought). It analyzes a customer review to estimate the
product rating, detect sentiment and aspects, flag urgency, generate a personalized
customer message, and produce a retail-team report — plus a dashboard summarizing
insights by product category and urgency.

## Setup

```bash
# from the project root, using the existing venv
.venv/Scripts/activate                 # Windows
pip install -r milestone2/requirements.txt

# add your Azure key
cp milestone2/.env.example milestone2/.env   # then paste AZURE_OPENAI_API_KEY
```

## Run the app

```bash
cd milestone2
streamlit run app.py
```

Tabs: **Analyze a Review** (single review → rating/sentiment/aspects/urgency + message +
report), **Batch Insights** (category × urgency dashboard), **Method Comparison**
(Zero/Few/CoT side by side).

## Modules

| File | Responsibility |
|---|---|
| `config.py` | Azure OpenAI chat client from `.env` |
| `schema.py` | `ReviewAnalysis` pydantic output schema |
| `prompts.py` | Zero-Shot / Few-Shot / CoT prompt builders |
| `examples.py` | Curated few-shot examples (mixed sentiment, multi-aspect) |
| `analyzer.py` | `analyze_review()` — prompt → LLM → structured result |
| `messaging.py` | Personalized customer message (Objective 3) |
| `reports.py` | Retail report + category/urgency summary (Objectives 4 & 2) |
| `app.py` | Streamlit UI |

## Experiments

`../Milestone2_Prompt_Engineering.ipynb` runs the three methods on a ~50-review sample,
compares accuracy against the Milestone-1 ground truth, and precomputes
`../analyzed_reviews.csv` used by the dashboard.
