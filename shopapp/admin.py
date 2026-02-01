from django.contrib import admin
from .models import Product, Platform, ProductListing, PriceHistory, AIInsight
from .services.openai_review_engine import generate_ai_review


@admin.action(description="Regenerate AI Review")
def regenerate_ai_review(modeladmin, request, queryset):
    for product in queryset:
        listings = ProductListing.objects.filter(product=product)
        if not listings.exists():
            continue

        ai_data = generate_ai_review(product, listings)

        AIInsight.objects.update_or_create(
            product=product,
            defaults={
                "pros": ai_data["pros"],
                "cons": ai_data["cons"],
                "verdict": ai_data["verdict"],
            }
        )

        product.rating = ai_data["rating"]
        product.save(update_fields=["rating"])


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "rating")
    actions = [regenerate_ai_review]


admin.site.register(Platform)
admin.site.register(ProductListing)
admin.site.register(PriceHistory)
admin.site.register(AIInsight)
