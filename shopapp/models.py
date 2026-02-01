from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255)
    image = models.URLField(blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.title


class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ProductListing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    price = models.FloatField()
    url = models.URLField()
    platform_rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.title} - {self.platform.name}"


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.price}"


class AIInsight(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)

    pros = models.JSONField(default=list)
    cons = models.JSONField(default=list)
    verdict = models.TextField()

    # ✅ ADDED (NO EXISTING LOGIC TOUCHED)
    deal_score = models.FloatField(null=True, blank=True)
    best_time_to_buy = models.CharField(max_length=50, null=True, blank=True)

    generated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI Insight - {self.product.title}"
