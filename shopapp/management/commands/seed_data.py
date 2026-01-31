from django.core.management.base import BaseCommand
from shopapp.models import (
    Product,
    Platform,
    ProductListing,
    AIInsight,
    PriceHistory
)
import random

class Command(BaseCommand):
    help = "Seed ShopSync data"

    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        Platform.objects.all().delete()

        amazon = Platform.objects.create(name="Amazon")
        flipkart = Platform.objects.create(name="Flipkart")
        apple = Platform.objects.create(name="Apple")

        items = ["iPhone 17 Pro Max", "Sony WH-1000XM6", "Air Jordan 1 Low OG"]

        for name in items:
            p = Product.objects.create(title=name)

            prices = []
            for platform in [amazon, flipkart, apple]:
                price = random.randint(40000, 150000)
                prices.append(price)
                ProductListing.objects.create(
                    product=p,
                    platform=platform,
                    price=price,
                    url="https://example.com",
                    rating=round(random.uniform(4.0, 5.0), 1)
                )

            AIInsight.objects.create(
                product=p,
                pros=["Premium quality", "Strong performance"],
                cons=["High price"],
                verdict="Recommended if budget allows"
            )

            for price in prices:
                PriceHistory.objects.create(product=p, price=price)

        self.stdout.write(self.style.SUCCESS("ShopSync data ready"))
