import asyncio
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

from storage.db import add_llm_tokens, get_month_usage
from utils import llm_cache
from utils.advanced_logging import get_logger
from utils.env import get
from utils.logger import setup_logging

load_dotenv()


# ---------------------------------------------------------------------------
# Build OpenAI/OpenRouter client once (module-level, reused across calls)
# ---------------------------------------------------------------------------
def get_client():
    """Get OpenAI client with proper environment variable loading"""
    base_url = (
        get("OPENROUTER_API_BASE")
        or get("OPENAI_API_BASE")
        or "https://api.openai.com/v1"
    )
    api_key = get("OPENROUTER_API_KEY") or get("OPENAI_API_KEY")

    if not api_key:
        logger.warning("No OpenAI/OpenRouter API key found in environment")
        return None

    return OpenAI(
        base_url=base_url,
        api_key=api_key,
    )


logger = get_logger(__name__)
logging.basicConfig(level=logging.INFO)
setup_logging()

PROMPT_TEMPLATE = (
    "Rewrite the post below in **degenerate crypto Twitter** style (memes, emojis, CT slang).\n"
    "Stay under 50 words and start with a punchy headline.\n\n"
    "Example original:\n"
    "Bitcoin ETF rumors pump the market as whales accumulate.\n\n"
    "Example rewrite:\n"
    "🚀 **BTC ETF Whispers Ignite Goblin-Mode Accumulation!** 🐳💰\n"
    "Whales scooping sats like it's the last dip. Pack bags or get left in fiat dust. LFG!\n\n"
    "Now rewrite: \n{content}\n\n"  # noqa: E501
)


def rewrite_content(item: dict[str, str]) -> dict[str, str]:
    """Rewrite a social-media item into a "degenerate crypto" summary.

    This helper performs **one** chat-completion (or grabs the cached answer)
    and returns a mapping with two keys:

    * ``headline`` – first line, ≤50 words.
    * ``body`` – optional body text (can be empty string).

    Guard-rails:
    * If no API key is configured (or monthly token budget exhausted) the
      original text is returned unmodified.
    * The prompt content is truncated to 1 000 chars to keep token cost
      predictable.
    * All LLM calls are cached in ``utils.llm_cache``.
    """
    content = item.get("full_text") or item.get("text") or item.get("summary") or ""
    prompt = PROMPT_TEMPLATE.format(content=content[:1000])

    client = get_client()
    if not client:
        logger.warning("No OpenAI/OpenRouter API key; returning original text")
        return {"headline": content[:50], "body": content}

    cost_per_1k = float(get("OPENROUTER_COST_PER_1K_USD", "0.005"))
    monthly_budget = float(get("LLM_BUDGET_MONTHLY_USD", "10"))
    from datetime import datetime

    month = datetime.utcnow().strftime("%Y-%m")
    usage = get_month_usage(month)

    est_tokens_prompt = int(len(prompt) / 4)

    # Determine if this request would exceed the monthly budget even when no usage row exists yet
    current_cost = usage.cost_usd if usage else 0.0
    projected_total = current_cost + (est_tokens_prompt / 1000) * cost_per_1k
    if projected_total > monthly_budget:
        logger.warning("LLM budget exceeded; returning original text")
        return {"headline": content[:50], "body": content}

    # check cache
    cached = llm_cache.get(prompt)
    if cached:
        rewritten = cached["text"]
        logger.debug("Rewrite cache hit", prompt_hash=hash(prompt))
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
            usage_tokens = est_tokens_prompt + int(len(rewritten) / 4)
            add_llm_tokens(usage_tokens, usage_tokens / 1000 * cost_per_1k)
            logger.info(
                "LLM rewrite completed",
                tokens=usage_tokens,
                cost_usd=usage_tokens / 1000 * cost_per_1k,
            )
        except Exception as exc:
            logger.error("LLM rewrite failed", exc_info=exc)
            rewritten = content

    parts = rewritten.split("\n", 1)
    if len(parts) == 2:
        headline, body = parts
    else:
        headline = parts[0]
        body = ""
    return {"headline": headline, "body": body}


async def _rewrite_single_item(item: dict[str, str], prompt: str) -> dict[str, str]:
    """Async helper for rewriting a single item"""
    client = get_client()
    if not client:
        logger.warning("No OpenAI/OpenRouter API key; returning original text")
        content = item.get("full_text") or item.get("text") or item.get("summary") or ""
        return {"headline": content[:50], "body": content}

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
        est_tokens_prompt = int(len(prompt) / 4)
        usage_tokens = est_tokens_prompt + int(len(rewritten) / 4)
        cost_per_1k = float(get("OPENROUTER_COST_PER_1K_USD", "0.005"))
        add_llm_tokens(usage_tokens, usage_tokens / 1000 * cost_per_1k)

        parts = rewritten.split("\n", 1)
        if len(parts) == 2:
            return {"headline": parts[0], "body": parts[1]}
        else:
            return {"headline": parts[0], "body": ""}
    except Exception as exc:
        logger.error("LLM rewrite failed for item: %s", exc)
        content = item.get("full_text") or item.get("text") or item.get("summary") or ""
        return {"headline": content[:50], "body": content}


def rewrite_batch(items: list[dict[str, str]]) -> list[dict[str, str]]:
    """Rewrite multiple items with improved caching and concurrent processing"""
    if not items:
        return []

    results: list[dict[str, str]] = [None] * len(items)  # type: ignore

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

    # Process uncached items with controlled concurrency
    semaphore = asyncio.Semaphore(5)  # Limit concurrent requests

    async def process_with_semaphore(idx: int):
        async with semaphore:
            return await _rewrite_single_item(items[idx], prompts[idx])

    async def process_all():
        tasks = [process_with_semaphore(idx) for idx in uncached_indices]
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, (idx, result) in enumerate(zip(uncached_indices, completed_results)):
            if isinstance(result, Exception):
                logger.error("Task failed for index %s: %s", idx, result)
                # Fallback to original content
                content = (
                    items[idx].get("full_text")
                    or items[idx].get("text")
                    or items[idx].get("summary")
                    or ""
                )
                results[idx] = {"headline": content[:50], "body": content}
            else:
                results[idx] = result

    # Run async processing
    try:
        asyncio.run(process_all())
    except Exception as exc:
        logger.error("Batch processing failed, falling back to sequential: %s", exc)
        # Fallback to sequential processing
        for idx in uncached_indices:
            try:
                results[idx] = rewrite_content(items[idx])
            except Exception as e:
                logger.error("Sequential processing failed for item %s: %s", idx, e)
                # Final fallback
                content = (
                    items[idx].get("full_text")
                    or items[idx].get("text")
                    or items[idx].get("summary")
                    or ""
                )
                results[idx] = {"headline": content[:50], "body": content}

    return results
