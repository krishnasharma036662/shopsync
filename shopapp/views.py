from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, "home.html")

@login_required
def search(request):
    return render(request, "search.html")

@login_required
def product(request, product_id):
    return render(request, "product.html", {"product_id": product_id})
