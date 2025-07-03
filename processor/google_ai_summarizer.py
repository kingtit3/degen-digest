#!/usr/bin/env python3
"""Google Cloud AI (Vertex AI) summarizer for Degen Digest"""

import os

from dotenv import load_dotenv
from google.cloud import aiplatform

from storage.db import add_llm_tokens, get_month_usage
from utils import llm_cache
from utils.advanced_logging import get_logger
from utils.env import get
from utils.logger import setup_logging

load_dotenv()

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

if project_id:
    aiplatform.init(project=project_id, location=location)

logger = get_logger(__name__)
setup_logging()

PROMPT_TEMPLATE = (
    "Rewrite the post below in **degenerate crypto Twitter** style (memes, emojis, CT slang).\n"
    "Stay under 50 words and start with a punchy headline.\n\n"
    "Example original:\n"
    "Bitcoin ETF rumors pump the market as whales accumulate.\n\n"
    "Example rewrite:\n"
    "🚀 **BTC ETF Whispers Ignite Goblin-Mode Accumulation!** 🐳💰\n"
    "Whales scooping sats like it's the last dip. Pack bags or get left in fiat dust. LFG!\n\n"
    "Now rewrite: \n{content}\n\n"
)


def rewrite_content(item: dict[str, str]) -> dict[str, str]:
    """Rewrite a social-media item using Google Cloud AI (Vertex AI).

    This function uses Google's Gemini model through Vertex AI to rewrite content
    in degenerate crypto style.
    """
    content = item.get("full_text") or item.get("text") or item.get("summary") or ""
    prompt = PROMPT_TEMPLATE.format(content=content[:1000])

    # Check if Google Cloud is configured
    if not project_id:
        logger.warning("No Google Cloud project configured; returning original text")
        return {"headline": content[:50], "body": content}

    # Budget check (similar to OpenRouter version)
    cost_per_1k = float(
        get("GOOGLE_AI_COST_PER_1K_USD", "0.000075")
    )  # Gemini Flash pricing
    monthly_budget = float(get("LLM_BUDGET_MONTHLY_USD", "10"))
    from datetime import datetime

    month = datetime.utcnow().strftime("%Y-%m")
    usage = get_month_usage(month)

    est_tokens_prompt = int(len(prompt) / 4)
    current_cost = usage.cost_usd if usage else 0.0
    projected_total = current_cost + (est_tokens_prompt / 1000) * cost_per_1k

    if projected_total > monthly_budget:
        logger.warning("LLM budget exceeded; returning original text")
        return {"headline": content[:50], "body": content}

    # Check cache
    cached = llm_cache.get(prompt)
    if cached:
        rewritten = cached["text"]
        logger.debug("Rewrite cache hit", prompt_hash=hash(prompt))
    else:
        try:
            # Use Vertex AI Gemini model
            model = aiplatform.GenerativeModel("gemini-1.5-flash")

            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.9,
                    "max_output_tokens": 120,
                },
            )

            rewritten = response.text.strip()
            llm_cache.set(prompt, {"text": rewritten})

            # Cost tracking
            usage_tokens = est_tokens_prompt + int(len(rewritten) / 4)
            add_llm_tokens(usage_tokens, usage_tokens / 1000 * cost_per_1k)
            logger.info(
                "Google AI rewrite completed",
                tokens=usage_tokens,
                cost_usd=usage_tokens / 1000 * cost_per_1k,
            )
        except Exception as exc:
            logger.error("Google AI rewrite failed", exc_info=exc)
            rewritten = content

    parts = rewritten.split("\n", 1)
    if len(parts) == 2:
        headline, body = parts
    else:
        headline = parts[0]
        body = ""
    return {"headline": headline, "body": body}


def rewrite_batch(items: list[dict[str, str]]) -> list[dict[str, str]]:
    """Rewrite multiple items using Google Cloud AI with batching"""
    results: list[dict[str, str]] = [None] * len(items)

    # Build prompts and check cache first
    prompts = [
        PROMPT_TEMPLATE.format(
            content=(it.get("full_text") or it.get("text") or it.get("summary") or "")[
                :1000
            ]
        )
        for it in items
    ]

    uncached_indices = []
    for idx, p in enumerate(prompts):
        cached = llm_cache.get(p)
        if cached:
            text = cached["text"]
            parts = text.split("\n", 1)
            results[idx] = {
                "headline": parts[0],
                "body": parts[1] if len(parts) == 2 else "",
            }
        else:
            uncached_indices.append(idx)

    if not uncached_indices:
        return results  # all cached

    # Process uncached items
    if project_id:
        try:
            model = aiplatform.GenerativeModel("gemini-1.5-flash")

            for idx in uncached_indices:
                try:
                    response = model.generate_content(
                        prompts[idx],
                        generation_config={
                            "temperature": 0.9,
                            "max_output_tokens": 120,
                        },
                    )

                    rewritten = response.text.strip()
                    llm_cache.set(prompts[idx], {"text": rewritten})

                    parts = rewritten.split("\n", 1)
                    results[idx] = {
                        "headline": parts[0],
                        "body": parts[1] if len(parts) == 2 else "",
                    }

                except Exception as exc:
                    logger.error(f"Failed to process item {idx}: {exc}")
                    content = (
                        items[idx].get("full_text")
                        or items[idx].get("text")
                        or items[idx].get("summary")
                        or ""
                    )
                    results[idx] = {"headline": content[:50], "body": content}
        except Exception as exc:
            logger.error(f"Batch processing failed: {exc}")
            # Fallback to individual processing
            for idx in uncached_indices:
                results[idx] = rewrite_content(items[idx])
    else:
        # Fallback to original content
        for idx in uncached_indices:
            content = (
                items[idx].get("full_text")
                or items[idx].get("text")
                or items[idx].get("summary")
                or ""
            )
            results[idx] = {"headline": content[:50], "body": content}

    return results
