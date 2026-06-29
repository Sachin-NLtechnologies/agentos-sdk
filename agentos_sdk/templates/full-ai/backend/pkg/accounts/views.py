from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def auth_csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})

@api_view(["POST"])
@permission_classes([AllowAny])
def auth_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({
            "username": user.username,
            "email": user.email,
            "isAuthenticated": True,
            "role": getattr(request.session, "aos_role", "VIEWER")
        })
    return Response({"detail": "Invalid credentials"}, status=400)

@api_view(["POST"])
def auth_logout(request):
    logout(request)
    return Response({"detail": "Successfully logged out"})

@api_view(["GET"])
def auth_me(request):
    user = request.user
    if user.is_authenticated:
        return Response({
            "username": user.username,
            "email": user.email,
            "isAuthenticated": True,
            "role": request.session.get("aos_role", "VIEWER")
        })
    return Response({"detail": "Not authenticated"}, status=401)
