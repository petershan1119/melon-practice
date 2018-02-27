from django.contrib.auth import authenticate, login, logout, get_user_model

from django.shortcuts import render, redirect


__all__ = (
    'logout_view',
)


def logout_view(request):
    logout(request)
    return redirect('index')