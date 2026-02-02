"""Serializers for import_export app."""
from rest_framework import serializers
from .models import CSVImport

class CSVImportSerializer(serializers.ModelSerializer):
    """Serializer for CSVImport model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = CSVImport
        fields = [
            'id', 'file_name', 'status', 'status_display',
            'total_rows', 'success_count', 'error_count',
            'progress', 'uploaded_at', 'started_at', 'completed_at',
            'uploaded_by_name'
        ]

    def get_progress(self, obj):
        if obj.total_rows == 0:
            return 0
        return int((obj.success_count + obj.error_count) / obj.total_rows * 100)

class CSVImportDetailSerializer(CSVImportSerializer):
    """Detailed serializer with errors."""
    class Meta(CSVImportSerializer.Meta):
        fields = CSVImportSerializer.Meta.fields + ['errors']
