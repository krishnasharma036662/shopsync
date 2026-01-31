import requests
import os
import re

SERP_API_KEY = os.getenv("SERP_API_KEY")


def _parse_price(price):
    if not price:
        return 0
    cleaned = re.sub(r"[^\d.]", "", price)
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def google_shopping_search(query):
    # If no API key, skip live fetch safely
    if not SERP_API_KEY:
        return []

    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_shopping",
            "q": query,
            "hl": "en",
            "gl": "in",
            "api_key": SERP_API_KEY,
        }

        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception:
        return []

    results = []

    for item in data.get("shopping_results", []):
        results.append({
            "title": item.get("title") or "Unknown Product",
            "price": _parse_price(item.get("price")),
            "platform": item.get("source") or "Unknown",
            "url": item.get("link") or "",
            "image": item.get("thumbnail"),
            "rating": item.get("rating") or 0,
        })

    return results
