from django.http import JsonResponse
from django.shortcuts import redirect
from .models import (
    Product,
    Platform,
    ProductListing,
    PriceHistory,
)
from .services.google_shopping import google_shopping_search


def trending(request):
    products = Product.objects.all()[:6]
    return JsonResponse(
        [{"id": p.id, "title": p.title} for p in products],
        safe=False
    )


def search_api(request):
    query = request.GET.get("q", "").strip()
    results = []

    # 1️⃣ Live Google Shopping
    if query:
        live_results = google_shopping_search(query)
        for item in live_results:
            product, _ = Product.objects.get_or_create(
                title=item["title"],
                defaults={
                    "image": item["image"],
                    "rating": item["rating"],
                },
            )

            platform, _ = Platform.objects.get_or_create(
                name=item["platform"]
            )

            ProductListing.objects.update_or_create(
                product=product,
                platform=platform,
                defaults={
                    "price": item["price"],
                    "url": item["url"],
                },
            )

            if item["price"] > 0:
                PriceHistory.objects.create(
                    product=product,
                    price=item["price"]
                )

            results.append({
                "id": product.id,
                "title": product.title
            })

    # 2️⃣ DB fallback
    if not results and query:
        db_products = Product.objects.filter(title__icontains=query)
        for p in db_products:
            results.append({
                "id": p.id,
                "title": p.title
            })

    return JsonResponse({"results": results})


def compare(request, product_id):
    product = Product.objects.get(id=product_id)
    listings = ProductListing.objects.filter(product=product)

    return JsonResponse({
        "product": product.title,
        "comparisons": [
            {
                "platform": l.platform.name,
                "price": l.price,
                # 🔥 IMPORTANT: referral redirect
                "url": f"/api/redirect/{l.id}/"
            }
            for l in listings
        ]
    })


def redirect_to_store(request, listing_id):
    listing = ProductListing.objects.filter(id=listing_id).first()
    if not listing or not listing.url:
        return redirect("/")

    # This is where affiliate tracking would happen
    return redirect(listing.url)


def insights(request, product_id):
    prices = list(
        PriceHistory.objects.filter(product_id=product_id)
        .order_by("-date")
        .values_list("price", flat=True)
    )

    verdict = "WAIT"
    if len(prices) >= 3 and prices[0] < sum(prices) / len(prices):
        verdict = "BUY NOW"

    return JsonResponse({
        "pros": ["Multiple sellers", "Live pricing"],
        "cons": ["Price fluctuation"],
        "verdict": verdict,
    })


def price_trend(request, product_id):
    history = PriceHistory.objects.filter(product_id=product_id).order_by("date")
    return JsonResponse({
        "dates": [h.date.isoformat() for h in history],
        "prices": [h.price for h in history],
    })
