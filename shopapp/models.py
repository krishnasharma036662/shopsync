from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    title = models.CharField(max_length=255, unique=True)
    image = models.URLField(null=True, blank=True)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.title


class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ProductListing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    url = models.URLField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)


class AIInsight(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    pros = models.JSONField(default=list)
    cons = models.JSONField(default=list)
    verdict = models.TextField()


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=10, default="dark")
