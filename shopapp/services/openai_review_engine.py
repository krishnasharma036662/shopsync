import os
import json
from openai import OpenAI
from openai import RateLimitError, APIError, APITimeoutError


def _get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def generate_ai_review(product, listings):
    """
    Uses OpenAI ONLY on live review signals.
    No scraping. No hallucination. No category guessing.
    """

    client = _get_client()
    if not client:
        return {
            "pros": [],
            "cons": [],
            "rating": 0,
            "verdict": "INSUFFICIENT DATA",
            "deal_score": 0,
            "best_time_to_buy": "INSUFFICIENT DATA",
        }

    if not listings:
        return {
            "pros": [],
            "cons": [],
            "rating": 0,
            "verdict": "INSUFFICIENT DATA",
            "deal_score": 0,
            "best_time_to_buy": "INSUFFICIENT DATA",
        }

    lines = []
    ratings = []
    prices = []

    for l in listings:
        if l.platform_rating and l.platform_rating > 0:
            ratings.append(l.platform_rating)

        if l.price and l.price > 0:
            prices.append(l.price)

        lines.append(
            f"- {l.platform.name}: rating {l.platform_rating}, reviews {l.review_count}, price {l.price}"
        )

    prompt = f"""
You are given live marketplace signals for a product.

Product: {product.title}

Platform data:
{chr(10).join(lines)}

Rules:
- Do NOT invent features or opinions
- Do NOT assume specifications
- Base analysis ONLY on ratings consistency, review counts, and price spread
- Be conservative if data is weak

Tasks:
1. List 2–4 pros inferred from the data
2. List 1–3 cons inferred from the data
3. Give a short neutral verdict
4. Give a deal_score from 0–10 (higher = better deal)
5. Decide best_time_to_buy: BUY NOW, WAIT, or MONITOR

Respond ONLY in valid JSON:
{{
  "pros": [],
  "cons": [],
  "verdict": "",
  "deal_score": 0,
  "best_time_to_buy": ""
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        raw_output = response.choices[0].message.content.strip()

        try:
            data = json.loads(raw_output)
        except Exception:
            data = {
                "pros": [],
                "cons": [],
                "verdict": "ANALYSIS UNAVAILABLE",
                "deal_score": 0,
                "best_time_to_buy": "MONITOR",
            }

    except (RateLimitError, APIError, APITimeoutError, Exception):
        # 🔒 HARD FAIL SAFE (NO 500s EVER)
        data = {
            "pros": [],
            "cons": [],
            "verdict": "AI TEMPORARILY UNAVAILABLE",
            "deal_score": 0,
            "best_time_to_buy": "MONITOR",
        }

    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0

    return {
        "pros": data.get("pros", []),
        "cons": data.get("cons", []),
        "verdict": data.get("verdict", ""),
        "rating": avg_rating,
        "deal_score": data.get("deal_score", 0),
        "best_time_to_buy": data.get("best_time_to_buy", "MONITOR"),
    }
