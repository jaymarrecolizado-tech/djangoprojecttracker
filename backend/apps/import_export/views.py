"""Views for import_export app."""
import os
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.conf import settings
from apps.common.responses import success_response, error_response, created_response
from apps.accounts.permissions import IsEditor
from .models import CSVImport
from .serializers import CSVImportSerializer, CSVImportDetailSerializer
from .tasks import process_csv_import

class ImportViewSet(viewsets.ModelViewSet):
    """ViewSet for CSV imports."""
    queryset = CSVImport.objects.all()
    serializer_class = CSVImportSerializer
    permission_classes = [IsEditor]
    parser_classes = [MultiPartParser]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CSVImportDetailSerializer
        return CSVImportSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload and process CSV file."""
        file = request.FILES.get('file')
        if not file:
            return error_response(message='No file provided')

        if not file.name.endswith('.csv'):
            return error_response(message='File must be a CSV')

        # Save file
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Create import record
        csv_import = CSVImport.objects.create(
            file_name=file.name,
            file_path=file_path,
            uploaded_by=request.user
        )

        # Start async processing
        process_csv_import.delay(str(csv_import.id))

        return created_response(
            data={'import': CSVImportSerializer(csv_import).data},
            message='File uploaded and processing started'
        )

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get import progress."""
        csv_import = self.get_object()
        return success_response(data={'import': CSVImportSerializer(csv_import).data})
