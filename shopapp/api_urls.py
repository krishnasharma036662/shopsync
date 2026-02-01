from django.urls import path
from . import api_views

urlpatterns = [
    path("trending/", api_views.trending),
    path("search/", api_views.search_api),
    path("compare/<int:product_id>/", api_views.compare),
    path("price-trend/<int:product_id>/", api_views.price_trend),
    path("insights/<int:product_id>/", api_views.insights),
    path("redirect/<int:listing_id>/", api_views.redirect_to_store),
]
