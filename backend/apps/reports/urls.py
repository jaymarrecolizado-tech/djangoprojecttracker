"""URLs for reports app."""
from django.urls import path
from .views import (
    StatisticsView, DistributionView, TimelineView,
    StatusReportView, DateRangeReportView, LocationReportView,
    ExportReportView
)

urlpatterns = [
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('distribution/', DistributionView.as_view(), name='distribution'),
    path('timeline/', TimelineView.as_view(), name='timeline'),
    path('status/', StatusReportView.as_view(), name='status_report'),
    path('date-range/', DateRangeReportView.as_view(), name='date_range_report'),
    path('location/', LocationReportView.as_view(), name='location_report'),
    path('export/', ExportReportView.as_view(), name='export_report'),
]
