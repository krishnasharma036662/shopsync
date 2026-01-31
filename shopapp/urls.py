from django.urls import path
from .views import home, search, product
from .auth_views import login_view, logout_view, signup_view

urlpatterns = [
    path('', home),
    path('search/', search),
    path('product/<int:product_id>/', product),
    path('login/', login_view),
    path('logout/', logout_view),
    path('signup/', signup_view),
]
