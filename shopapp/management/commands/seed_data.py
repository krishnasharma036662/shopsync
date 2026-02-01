from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from shopapp.models import (
    Product,
    Platform,
    ProductListing,
    PriceHistory,
    AIInsight,
)


class Command(BaseCommand):
    help = "Seed demo data with valid multi-day price history"

    def handle(self, *args, **kwargs):
        self.stdout.write("⏳ Seeding demo data...")

        ProductListing.objects.all().delete()
        PriceHistory.objects.all().delete()
        AIInsight.objects.all().delete()
        Product.objects.all().delete()
        Platform.objects.all().delete()

        platforms = ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Vijay Sales"]
        platform_objs = {p: Platform.objects.create(name=p) for p in platforms}

        products = [
            {
                "title": "Fastrack Men's Automatic Analog Watch",
                "image": "",
            }
        ]

        for pdata in products:
            product = Product.objects.create(
                title=pdata["title"],
                image=pdata["image"],
                rating=4.2,
            )

            base_price = random.randint(8000, 15000)

            for name, platform in platform_objs.items():
                listing = ProductListing.objects.create(
                    product=product,
                    platform=platform,
                    price=base_price + random.randint(-2000, 2000),
                    url=f"https://{name.lower().replace(' ', '')}.com/search?q={product.title.replace(' ', '+')}",
                    platform_rating=random.uniform(3.5, 4.7),
                    review_count=random.randint(100, 3000),
                )

                for i in range(7):
                    PriceHistory.objects.create(
                        product=product,
                        price=listing.price + random.randint(-1500, 1500),
                        created_at=timezone.now() - timedelta(days=6 - i),
                    )

            AIInsight.objects.create(
                product=product,
                pros=["Multiple sellers", "Competitive pricing"],
                cons=["Price fluctuations"],
                verdict="WAIT",
            )

        self.stdout.write(self.style.SUCCESS("✅ Demo data seeded correctly"))
