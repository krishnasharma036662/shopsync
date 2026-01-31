from django.contrib import admin
from .models import (
    Product,
    Platform,
    ProductListing,
    PriceHistory,
    AIInsight,
    UserPreference,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "rating")
    search_fields = ("title",)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    list_display = ("product", "platform", "price", "last_updated")
    list_filter = ("platform",)
    search_fields = ("product__title",)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("product", "price", "date")
    list_filter = ("date",)


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ("product", "verdict")


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "theme")
