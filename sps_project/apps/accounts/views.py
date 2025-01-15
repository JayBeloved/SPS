# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import LoginForm #SignUpForm


def home_view(request):
    return HttpResponseRedirect(reverse('login'))

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("core:dashboard")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

def logout_view(request):
    logout(request)
    return redirect('login')