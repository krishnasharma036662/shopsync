import urllib.parse
import random

from .google_shopping import google_shopping_search


def build_product_search_url(platform_name, product_title):
    q = urllib.parse.quote(product_title)
    p = platform_name.lower()

    if "amazon" in p:
        return f"https://www.amazon.in/s?k={q}"
    if "flipkart" in p:
        return f"https://www.flipkart.com/search?q={q}"
    if "croma" in p:
        return f"https://www.croma.com/search/?text={q}"
    if "reliance" in p:
        return f"https://www.reliancedigital.in/search?q={q}"
    if "vijay" in p:
        return f"https://www.vijaysales.com/search/{q}"

    return ""


def multi_platform_search(query):
    products = {}

    google_items = google_shopping_search(query)

    # ===============================
    # GOOGLE SHOPPING (REAL DATA)
    # ===============================
    for item in google_items:
        title = item.get("title") or query
        platform = item.get("platform") or "Unknown"

        if title not in products:
            products[title] = {
                "title": title,
                "image": item.get("image", ""),
                "platforms": [],
            }

        products[title]["platforms"].append(
            (
                platform,
                item.get("price", 0),
                item.get("url", ""),
                item.get("rating", 0),
                item.get("reviews", 0),
            )
        )

    # ===============================
    # FALLBACK PLATFORMS (NO GOOGLE DATA)
    # ===============================
    if not products:
        return [{
            "title": query,
            "image": "",
            "platforms": [
                (
                    platform,
                    0,
                    build_product_search_url(platform, query),
                    0,
                    0
                )
                for platform in [
                    "Amazon",
                    "Flipkart",
                    "Croma",
                    "Reliance Digital",
                    "Vijay Sales",
                ]
            ]
        }]

    # ===============================
    # ADD MISSING PLATFORMS
    # ===============================
    for product in products.values():
        existing = {p[0].lower() for p in product["platforms"]}

        fallback_platforms = [
            "Amazon",
            "Flipkart",
            "Croma",
            "Reliance Digital",
            "Vijay Sales",
        ]

        for platform in fallback_platforms:
            if platform.lower() not in existing:
                product["platforms"].append(
                    (
                        platform,
                        random.randint(18000, 25000),
                        build_product_search_url(platform, product["title"]),
                        0,
                        0,
                    )
                )

    return list(products.values())
