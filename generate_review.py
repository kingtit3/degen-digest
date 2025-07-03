import os
from datetime import date
from pathlib import Path

import main as _digest
from processor.scorer import degen_score
from utils.advanced_logging import get_logger
from utils.pdf import md_to_pdf

logger = get_logger(__name__)
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
PDF_PATH = OUTPUT_DIR / f"review-{date.today().isoformat()}.pdf"


def build_review_md() -> str:
    sources = _digest.load_raw_sources()
    all_items = []
    for items in sources.values():
        all_items.extend(items)
    processed = _digest.process_items(all_items)

    # ---------------- Executive Summary (LLM) -----------------------------
    synopsis = ""
    try:
        from processor.summarizer import client as _llm_client  # type: ignore

        prompt = (
            "Write a comprehensive 250-300 word crypto market analysis covering these headlines. "
            "Use professional financial language and provide insights on market trends, "
            "key developments, potential impacts, and what investors should watch for. "
            "Structure it like a professional market report: \n"
            + "\n".join(h["headline"] for h in processed[:10])
        )
        _resp = _llm_client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=350,
        )
        synopsis = _resp.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Synopsis generation failed: %s", exc)
        synopsis = "*(Comprehensive market analysis unavailable)*"

    # ---------------- Viral & Up-and-coming ------------------------------
    top_viral = processed[:15]  # Increased from 10 to 15

    upcoming: list[tuple[int, dict]] = []
    for it in all_items:
        if not isinstance(it, dict):
            continue
        score = degen_score(it)
        likes = it.get("likeCount", 0)
        if score > 70 and likes < 50:  # Adjusted criteria
            upcoming.append((score, it))
    upcoming.sort(key=lambda x: x[0], reverse=True)
    upcoming = upcoming[:15]  # Increased from 10 to 15

    # ---------------- Buzz Acceleration ---------------------------------
    try:
        import processor.buzz as _buzz

        recent, prev = _buzz._load_two_latest()  # type: ignore (private ok)
        ratios = []
        for term, cnt in recent.items():
            prev_cnt = prev.get(term, 0)
            if cnt < 3:
                continue  # ignore tiny counts
            ratio = cnt / (prev_cnt or 0.1)
            if ratio < 1.3:  # Lowered threshold
                continue
            ratios.append((ratio, term, cnt, prev_cnt))
        ratios.sort(reverse=True)
        top_terms = ratios[:15]  # Increased from 10 to 15
    except Exception as exc:
        logger.warning("Buzz acceleration unavailable: %s", exc)
        top_terms = []

    # --------------------------------------------------------------------
    md_lines: list[str] = []
    md_lines.append("# 📈 Degen Digest – Comprehensive Market Review\n")
    md_lines.append(f"**Date:** {date.today().strftime('%B %d, %Y')}\n")
    md_lines.append("**Report Type:** Daily Market Analysis\n")
    md_lines.append(f"**Data Coverage:** {len(all_items)} total stories analyzed\n\n")

    # Executive summary
    md_lines.append("## 📋 Executive Summary\n")
    md_lines.append(synopsis + "\n")
    md_lines.append("\n---\n\n")

    # Market Statistics
    md_lines.append("## 📊 Market Statistics\n\n")
    md_lines.append("**Engagement Analysis:**\n")
    engagement_scores = [
        item.get("_engagement_score", 0)
        for item in processed
        if item.get("_engagement_score")
    ]
    if engagement_scores:
        md_lines.append(
            f"- Average Engagement Score: {sum(engagement_scores)/len(engagement_scores):.2f}\n"
        )
        md_lines.append(f"- Highest Engagement Score: {max(engagement_scores):.2f}\n")
        md_lines.append(f"- Lowest Engagement Score: {min(engagement_scores):.2f}\n")

    # Source distribution
    source_counts = {}
    for item in all_items:
        if isinstance(item, dict):
            source = item.get("_source", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1

    md_lines.append("\n**Content Source Distribution:**\n")
    for source, count in sorted(
        source_counts.items(), key=lambda x: x[1], reverse=True
    ):
        source_name = source.title()
        percentage = (count / len(all_items)) * 100
        md_lines.append(f"- {source_name}: {count} stories ({percentage:.1f}%)\n")

    md_lines.append("\n---\n\n")

    # Top viral stories with full context
    md_lines.append("## 🔥 Top Viral Stories (Ranked by Engagement)\n\n")
    for idx, it in enumerate(top_viral, 1):
        md_lines.append(f"### {idx}. {it['headline']}\n\n")
        md_lines.append(f"**Category:** {it['tag']}\n\n")
        md_lines.append(f"**Full Content:** {it['body']}\n\n")

        # Engagement metrics
        metrics = []
        if it.get("likeCount"):
            metrics.append(f"Likes: {it['likeCount']:,}")
        if it.get("retweetCount"):
            metrics.append(f"Retweets: {it['retweetCount']:,}")
        if it.get("replyCount"):
            metrics.append(f"Replies: {it['replyCount']:,}")
        if it.get("viewCount"):
            metrics.append(f"Views: {it['viewCount']:,}")
        if it.get("_engagement_score"):
            metrics.append(f"Engagement Score: {it['_engagement_score']:.1f}")
        if it.get("_predicted_viral_score"):
            metrics.append(f"Viral Prediction: {it['_predicted_viral_score']:.1f}")

        if metrics:
            md_lines.append(f"**Performance Metrics:** {', '.join(metrics)}\n\n")

        # Source information
        source = it.get("_source", "Unknown").title()
        md_lines.append(f"**Source:** {source}\n\n")

        if it["link"]:
            md_lines.append(f"**Reference Link:** [{it['link']}]({it['link']})\n\n")

        md_lines.append("---\n\n")

    md_lines.append("\n\\newpage\n\n")

    # Trending terms with analysis
    md_lines.append("## 📈 Trending Terms & Hashtags Analysis\n\n")
    md_lines.append("**Hourly Acceleration Metrics:**\n\n")
    if top_terms:
        md_lines.append(
            "| Term | Hourly Change | Current Count | Previous Hour | Acceleration Ratio |\n"
        )
        md_lines.append(
            "|------|---------------|---------------|---------------|-------------------|\n"
        )
        for ratio, term, cnt, prev_cnt in top_terms:
            change = cnt - prev_cnt
            change_str = f"+{change}" if change > 0 else str(change)
            md_lines.append(
                f"| {term.upper()} | {change_str} | {cnt} | {prev_cnt} | {ratio:.1f}× |\n"
            )

        md_lines.append(
            "\n**Analysis:** Terms showing significant acceleration may indicate emerging trends or narratives in the crypto market.\n"
        )
    else:
        md_lines.append("*(No significant acceleration data available)*\n")
    md_lines.append("\n---\n\n")

    # Up-and-coming posts with context
    md_lines.append("## 🚀 Emerging Stories (High Potential)\n\n")
    md_lines.append(
        "**Note:** These stories show high engagement potential but haven't yet reached viral status.\n\n"
    )
    for idx, (score, raw) in enumerate(upcoming, 1):
        text = raw.get("full_text") or raw.get("text") or raw.get("title", "")
        head = text.strip().split("\n")[0][:120]  # Increased length
        link = raw.get("url") or raw.get("link") or raw.get("twitterUrl")

        md_lines.append(f"### {idx}. {head}\n\n")
        md_lines.append(f"**Predicted Engagement Score:** {score}\n\n")

        # Add source context
        source = raw.get("_source", "Unknown").title()
        md_lines.append(f"**Source:** {source}\n\n")

        if link:
            md_lines.append(f"**Link:** [{link}]({link})\n\n")

        md_lines.append("---\n\n")

    md_lines.append("\n\\newpage\n\n")

    # Market sentiment analysis
    md_lines.append("## 📊 Market Sentiment Analysis\n\n")

    # Calculate sentiment distribution
    positive_items = [
        item for item in processed if item.get("_sentiment_score", 0) > 0.1
    ]
    negative_items = [
        item for item in processed if item.get("_sentiment_score", 0) < -0.1
    ]
    neutral_items = [
        item for item in processed if abs(item.get("_sentiment_score", 0)) <= 0.1
    ]

    md_lines.append("**Overall Sentiment Distribution:**\n")
    md_lines.append(
        f"- Positive Sentiment: {len(positive_items)} stories ({len(positive_items)/len(processed)*100:.1f}%)\n"
    )
    md_lines.append(
        f"- Neutral Sentiment: {len(neutral_items)} stories ({len(neutral_items)/len(processed)*100:.1f}%)\n"
    )
    md_lines.append(
        f"- Negative Sentiment: {len(negative_items)} stories ({len(negative_items)/len(processed)*100:.1f}%)\n\n"
    )

    # Top positive and negative stories
    if positive_items:
        md_lines.append("**Top Positive Stories:**\n")
        for item in positive_items[:5]:
            md_lines.append(
                f"- {item['headline']} (Sentiment: {item.get('_sentiment_score', 0):.2f})\n"
            )
        md_lines.append("\n")

    if negative_items:
        md_lines.append("**Top Negative Stories:**\n")
        for item in negative_items[:5]:
            md_lines.append(
                f"- {item['headline']} (Sentiment: {item.get('_sentiment_score', 0):.2f})\n"
            )
        md_lines.append("\n")

    md_lines.append("---\n\n")

    # Complete reference section
    md_lines.append("## 📚 Complete Reference Library\n\n")
    md_lines.append("**All analyzed content sources organized by platform:**\n\n")

    # Group by source
    source_groups = {}
    for it in processed:
        if it["link"]:
            source = it.get("_source", "other")
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(it["link"])

    for source, links in source_groups.items():
        source_name = source.title()
        md_lines.append(f"**{source_name} Sources ({len(links)} links):**\n")
        for link in links:
            md_lines.append(f"- {link}\n")
        md_lines.append("\n")

    # Footer with disclaimers
    md_lines.append("---\n\n")
    md_lines.append("## ⚠️ Important Disclaimers\n\n")
    md_lines.append(
        "**Investment Risk Warning:** This report is for informational purposes only and does not constitute financial advice. "
        "Cryptocurrency investments carry significant risk, including the potential for total loss of capital.\n\n"
    )
    md_lines.append(
        "**Data Accuracy:** While we strive for accuracy, market data and social media content can be volatile and subject to rapid change.\n\n"
    )
    md_lines.append(
        "**Not Financial Advice:** Always conduct your own research and consider consulting with qualified financial advisors before making investment decisions.\n\n"
    )
    md_lines.append(
        f"**Report Generated:** {date.today().strftime('%B %d, %Y at %H:%M UTC')}\n"
    )
    md_lines.append(
        "**Data Sources:** Twitter, Reddit, Telegram, News APIs, CoinGecko\n"
    )

    return "\n".join(md_lines)


def main():
    md = build_review_md()
    md_file = OUTPUT_DIR / "review_tmp.md"
    md_file.write_text(md)
    md_to_pdf(md_file, PDF_PATH)
    logger.info("Review PDF generated", path=str(PDF_PATH))


if __name__ == "__main__":
    main()
