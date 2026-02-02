"""
URL configuration for the accounts app.

This module defines URL patterns for authentication and user management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CurrentUserView,
    LoginView,
    LogoutView,
    UserViewSet,
)

# Create a router for UserViewSet
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# URL patterns
urlpatterns = [
    # Authentication endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', CurrentUserView.as_view(), name='current-user'),

    # User management endpoints
    path('', include(router.urls)),
]
