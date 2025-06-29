from processor.summarizer import rewrite_content
from utils.env import get
import os


def test_budget_guardrail(monkeypatch):
    # set very low budget
    monkeypatch.setenv("LLM_BUDGET_MONTHLY_USD", "0.0001")
    monkeypatch.setenv("OPENROUTER_COST_PER_1K_USD", "0.01")

    # ensure no api key so summarizer will skip anyway
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    item = {"text": "Sample text"}
    result = rewrite_content(item)
    assert result["headline"].startswith("Sample") 