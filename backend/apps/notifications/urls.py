"""URLs for notifications app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, MarkAsReadView, MarkAllReadView, NotificationCountView

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('mark-read/<uuid:notification_id>/', MarkAsReadView.as_view(), name='mark_notification_read'),
    path('mark-all-read/', MarkAllReadView.as_view(), name='mark_all_read'),
    path('count/', NotificationCountView.as_view(), name='notification_count'),
]
