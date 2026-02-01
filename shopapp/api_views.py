from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlparse, parse_qs, unquote

from .models import Product, Platform, ProductListing, PriceHistory, AIInsight
from .services.multi_platform_search import multi_platform_search
from .services.openai_review_engine import generate_ai_review


# =========================
# HELPER
# =========================
def extract_real_product_url(url: str) -> str:
    if not url:
        return ""

    parsed = urlparse(url)

    if "google." in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "adurl" in qs:
            return unquote(qs["adurl"][0])

    return url


# =========================
# TRENDING
# =========================
def trending(request):
    products = Product.objects.all().order_by("-id")[:8]
    data = []

    for p in products:
        listings = ProductListing.objects.filter(product=p)
        prices = [l.price for l in listings if l.price > 0]

        data.append({
            "id": p.id,
            "title": p.title,
            "image": p.image or "",
            "rating": p.rating,
            "price": min(prices) if prices else None,
            "old_price": max(prices) if len(prices) > 1 else None,
        })

    return JsonResponse(data, safe=False)


# =========================
# SEARCH  ✅ RESTORED
# =========================
def search_api(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})

    catalog = multi_platform_search(query)
    results = []

    for item in catalog:
        product, _ = Product.objects.get_or_create(
            title=item["title"],
            defaults={"image": item.get("image")}
        )

        if item.get("image") and not product.image:
            product.image = item["image"]
            product.save(update_fields=["image"])

        prices = []

        for p in item["platforms"]:
            name, price, url, rating, reviews = p
            clean_url = extract_real_product_url(url)

            platform, _ = Platform.objects.get_or_create(name=name)

            ProductListing.objects.update_or_create(
                product=product,
                platform=platform,
                defaults={
                    "price": price,
                    "url": clean_url,
                    "platform_rating": rating,
                    "review_count": reviews,
                }
            )

            if price and price > 0:
                prices.append(price)

            PriceHistory.objects.create(
                product=product,
                price=price
            )

        results.append({
            "id": product.id,
            "title": product.title,
            "image": product.image or "",
            "description": "",
            "price": min(prices) if prices else None,
            "old_price": max(prices) if len(prices) > 1 else None,
        })

    return JsonResponse({"results": results})


# =========================
# COMPARE
# =========================
def compare(request, product_id):
    product = Product.objects.get(id=product_id)

    listings = (
        ProductListing.objects
        .filter(product=product, price__gt=0)
        .order_by("price")
    )

    seen = set()
    comparisons = []

    for l in listings:
        if l.platform.name in seen:
            continue
        seen.add(l.platform.name)

        comparisons.append({
            "platform": l.platform.name,
            "price": l.price,
            "listing_id": l.id
        })

    return JsonResponse({
        "product": product.title,
        "image": product.image or "",
        "comparisons": comparisons
    })


# =========================
# PRICE TREND
# =========================
def price_trend(request, product_id):
    history = (
        PriceHistory.objects
        .filter(product_id=product_id)
        .order_by("created_at")
    )

    if history.count() < 2:
        return JsonResponse({"dates": [], "prices": []})

    return JsonResponse({
        "dates": [h.created_at.strftime("%Y-%m-%d") for h in history],
        "prices": [h.price for h in history],
    })


# =========================
# INSIGHTS (LOCAL + AI)
# =========================
def insights(request, product_id):
    product = Product.objects.get(id=product_id)
    listings = ProductListing.objects.filter(product=product, price__gt=0)
    now = timezone.now()

    # ---------- LOCAL DEAL SCORE ----------
    prices = [l.price for l in listings]
    sellers = listings.count()

    deal_score = None
    best_time = None

    if prices:
        min_p = min(prices)
        max_p = max(prices)

        spread = (max_p - min_p) / max_p if max_p else 0
        seller_bonus = min(sellers, 5)

        deal_score = round(min(10, (spread * 10) + seller_bonus))

        if deal_score >= 7:
            best_time = "BUY NOW"
        elif deal_score >= 4:
            best_time = "MONITOR"
        else:
            best_time = "WAIT"

    # ---------- CACHED AI ----------
    insight = AIInsight.objects.filter(product=product).first()
    if insight and (now - insight.generated_at) < timedelta(days=7):
        return JsonResponse({
            "pros": insight.pros,
            "cons": insight.cons,
            "verdict": insight.verdict,
            "deal_score": deal_score,
            "best_time_to_buy": best_time,
        })

    # ---------- TRY AI ----------
    ai = generate_ai_review(product, listings)

    if ai["verdict"] in ["INSUFFICIENT DATA", "AI TEMPORARILY UNAVAILABLE"]:
        return JsonResponse({
            "pros": [],
            "cons": [],
            "verdict": "",
            "deal_score": deal_score,
            "best_time_to_buy": best_time,
        })

    insight, _ = AIInsight.objects.update_or_create(
        product=product,
        defaults={
            "pros": ai["pros"],
            "cons": ai["cons"],
            "verdict": ai["verdict"],
        }
    )

    product.rating = ai["rating"]
    product.save(update_fields=["rating"])

    return JsonResponse({
        "pros": insight.pros,
        "cons": insight.cons,
        "verdict": insight.verdict,
        "deal_score": ai.get("deal_score", deal_score),
        "best_time_to_buy": ai.get("best_time_to_buy", best_time),
    })


# =========================
# REDIRECT
# =========================
def redirect_to_store(request, listing_id):
    listing = ProductListing.objects.filter(id=listing_id).first()
    if not listing or not listing.url:
        return redirect("/")
    return redirect(listing.url)
