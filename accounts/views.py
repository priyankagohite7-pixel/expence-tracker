from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def register(request):
    if request.user.is_authenticated:
        return redirect('expenses:dashboard')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.first_name or user.username}!')
        return redirect('expenses:dashboard')
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('expenses:dashboard')
    form = LoginForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get('next', 'expenses:dashboard')
        return redirect(next_url)
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
