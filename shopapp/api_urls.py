from django.urls import path
from .api_views import (
    trending,
    search_api,
    compare,
    insights,
    price_trend,
    redirect_to_store,
)

urlpatterns = [
    path("trending/", trending),
    path("search/", search_api),
    path("compare/<int:product_id>/", compare),
    path("insights/<int:product_id>/", insights),
    path("trend/<int:product_id>/", price_trend),
    path("redirect/<int:listing_id>/", redirect_to_store),
]
