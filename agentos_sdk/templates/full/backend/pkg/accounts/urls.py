from django.urls import path
from agentos_sdk.django_auth import sso_urls
from . import views

urlpatterns = sso_urls("auth/agentos/") + [
    path("auth/csrf/", views.auth_csrf, name="auth-csrf"),
    path("auth/login/", views.auth_login, name="auth-login"),
    path("auth/logout/", views.auth_logout, name="auth-logout"),
    path("auth/me/", views.auth_me, name="auth-me"),
]
