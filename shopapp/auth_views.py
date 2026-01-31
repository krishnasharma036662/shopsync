from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/login/")


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html")

        user = User.objects.create_user(
            username=username,
            password=password1
        )

        login(request, user)
        return redirect("/")

    return render(request, "signup.html")
