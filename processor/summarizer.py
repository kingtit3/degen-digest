import os
from typing import Dict
import logging
from dotenv import load_dotenv
from openai import OpenAI
from utils.logger import setup_logging
from utils import llm_cache
from storage.db import add_llm_tokens, get_month_usage
from utils.env import get

load_dotenv()

# Build OpenAI/OpenRouter client once
client = OpenAI(
    base_url=os.getenv("OPENROUTER_API_BASE") or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1",
    api_key=os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
setup_logging()

PROMPT_TEMPLATE = (
    "Rewrite this post in a degenerate crypto voice. Add memes, emojis, CT slang."
    " Make it under 50 words and give it a funny headline.\n\nOriginal:\n{content}\n\n"  # noqa: E501
)

# single rewrite using cache
def rewrite_content(item: Dict[str, str]) -> Dict[str, str]:
    """Return dict with 'headline' and 'body' keys."""
    content = item.get("full_text") or item.get("text") or item.get("summary") or ""
    prompt = PROMPT_TEMPLATE.format(content=content[:1000])

    if client.api_key is None:
        logger.warning("No OpenAI/OpenRouter API key; returning original text")
        return {"headline": content[:50], "body": content}

    cost_per_1k = float(get("OPENROUTER_COST_PER_1K_USD", "0.005"))
    monthly_budget = float(get("LLM_BUDGET_MONTHLY_USD", "10"))
    from datetime import datetime
    month = datetime.utcnow().strftime("%Y-%m")
    usage = get_month_usage(month)

    est_tokens_prompt = int(len(prompt) / 4)

    if usage and usage.cost_usd + (est_tokens_prompt / 1000) * cost_per_1k > monthly_budget:
        logger.warning("LLM budget exceeded; returning original text")
        return {"headline": content[:50], "body": content}

    # check cache
    cached = llm_cache.get(prompt)
    if cached:
        rewritten = cached["text"]
    else:
        try:
            completion = client.chat.completions.create(
                model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=120,
            )
            rewritten = completion.choices[0].message.content.strip()
            llm_cache.set(prompt, {"text": rewritten})

            # cost tracking
            usage_tokens = est_tokens_prompt + int(len(rewritten)/4)
            add_llm_tokens(usage_tokens, usage_tokens/1000*cost_per_1k)
        except Exception as exc:
            logger.error("LLM rewrite failed: %s", exc)
            rewritten = content

    parts = rewritten.split("\n", 1)
    if len(parts) == 2:
        headline, body = parts
    else:
        headline = parts[0]
        body = ""
    return {"headline": headline, "body": body}

# batch rewrite to save cost/latency
def rewrite_batch(items: list[Dict[str, str]]) -> list[Dict[str, str]]:
    results: list[Dict[str, str]] = [None] * len(items)  # type: ignore

    # Build prompts and check cache first
    prompts = [PROMPT_TEMPLATE.format(content=(it.get("full_text") or it.get("text") or it.get("summary") or "")[:1000]) for it in items]

    uncached_indices = []
    for idx, p in enumerate(prompts):
        cached = llm_cache.get(p)
        if cached:
            text = cached["text"]
            parts = text.split("\n",1)
            results[idx] = {"headline": parts[0], "body": parts[1] if len(parts)==2 else ""}
        else:
            uncached_indices.append(idx)

    if not uncached_indices:
        return results  # all cached

    # Prepare messages list
    messages = [[{"role": "user", "content": prompts[i]}] for i in uncached_indices]

    try:
        completion = client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
            messages=messages,  # type: ignore
            temperature=0.9,
            max_tokens=120,
            batch=True,
        )
        for offset, idx in enumerate(uncached_indices):
            rewritten = completion.choices[offset].message.content.strip()
            llm_cache.set(prompts[idx], {"text": rewritten})
            parts = rewritten.split("\n",1)
            results[idx] = {"headline": parts[0], "body": parts[1] if len(parts)==2 else ""}
    except Exception as exc:
        logger.error("Batch LLM call failed: %s", exc)
        for idx in uncached_indices:
            results[idx] = rewrite_content(items[idx])  # fallback

    return results 