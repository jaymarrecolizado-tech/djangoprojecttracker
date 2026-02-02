"""URLs for reports app."""
from django.urls import path
from .views import StatisticsView, DistributionView, TimelineView

urlpatterns = [
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('distribution/', DistributionView.as_view(), name='distribution'),
    path('timeline/', TimelineView.as_view(), name='timeline'),
]
