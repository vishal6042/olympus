"""Azure OpenAI configuration for the ChicStyle feedback-intelligence system.

Loads credentials from `.env` and exposes a single shared `llm` (chat model).
No embeddings / vector store are used — Milestone 2 is prompt-engineering only.
"""
import os
import warnings
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Suppress a benign pydantic serialization warning emitted by langchain's
# `with_structured_output` when it serializes its internal `parsed` field.
warnings.filterwarnings("ignore", message="Pydantic serializer warnings", category=UserWarning)

# Load Azure OpenAI settings from the .env next to this file, so it works whether the
# app is run from milestone2/ or the notebook is run from the project root.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Chat model used for review analysis, message generation, and reports.
# `azure_deployment` maps to AZURE_LLM_MODEL (the Azure deployment name).
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_deployment=os.getenv("AZURE_LLM_MODEL"),
    temperature=0.2,  # low temperature -> consistent, deterministic analysis
)
