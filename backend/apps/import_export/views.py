"""Views for import_export app."""
import csv
import io
import os
import pandas as pd
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.conf import settings
from django.http import HttpResponse
from apps.common.responses import success_response, error_response, created_response
from apps.accounts.permissions import IsEditor
from .models import CSVImport
from .serializers import CSVImportSerializer, CSVImportDetailSerializer
from .tasks import process_csv_import
from apps.projects.models import ProjectSite
from apps.projects.serializers import ProjectSiteSerializer


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


class ExportViewSet(viewsets.ViewSet):
    """ViewSet for exporting projects."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List available export options."""
        return success_response(data={
            'formats': ['csv', 'excel'],
            'filters': ['status', 'project_type', 'province', 'municipality', 'barangay']
        })

    @action(detail=False, methods=['get'])
    def projects(self, request):
        """Export projects with optional filtering."""
        from django.db.models import Prefetch
        
        # Get query parameters for filtering
        status_filter = request.query_params.get('status')
        project_type_id = request.query_params.get('project_type')
        province_id = request.query_params.get('province')
        municipality_id = request.query_params.get('municipality')
        barangay_id = request.query_params.get('barangay')
        format_type = request.query_params.get('format', 'csv').lower()

        # Build queryset with filters
        queryset = ProjectSite.objects.filter(is_deleted=False).select_related(
            'project_type', 'barangay', 'municipality', 'province', 'created_by', 'updated_by'
        )

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if project_type_id:
            queryset = queryset.filter(project_type_id=project_type_id)
        if province_id:
            queryset = queryset.filter(province_id=province_id)
        if municipality_id:
            queryset = queryset.filter(municipality_id=municipality_id)
        if barangay_id:
            queryset = queryset.filter(barangay_id=barangay_id)

        # Serialize data
        data = ProjectSiteSerializer(queryset, many=True).data

        # Export based on format
        if format_type == 'excel':
            return self._export_excel(data)
        else:
            return self._export_csv(data)

    def _export_csv(self, data):
        """Export data to CSV format."""
        if not data:
            return error_response(message='No data to export')

        # Define CSV headers
        headers = [
            'site_code', 'site_name', 'project_type', 'barangay', 
            'municipality', 'province', 'latitude', 'longitude',
            'activation_date', 'status', 'remarks', 'created_at', 'updated_at'
        ]

        # Create CSV content
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()

        for item in data:
            row = {
                'site_code': item.get('site_code', ''),
                'site_name': item.get('site_name', ''),
                'project_type': item.get('project_type', {}).get('name', '') if item.get('project_type') else '',
                'barangay': item.get('barangay', {}).get('name', '') if item.get('barangay') else '',
                'municipality': item.get('municipality', {}).get('name', '') if item.get('municipality') else '',
                'province': item.get('province', {}).get('name', '') if item.get('province') else '',
                'latitude': item.get('latitude', ''),
                'longitude': item.get('longitude', ''),
                'activation_date': item.get('activation_date', ''),
                'status': item.get('status', ''),
                'remarks': item.get('remarks', ''),
                'created_at': item.get('created_at', ''),
                'updated_at': item.get('updated_at', ''),
            }
            writer.writerow(row)

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projects_export.csv"'
        return response

    def _export_excel(self, data):
        """Export data to Excel format."""
        if not data:
            return error_response(message='No data to export')

        # Flatten data for Excel
        rows = []
        for item in data:
            rows.append({
                'Site Code': item.get('site_code', ''),
                'Site Name': item.get('site_name', ''),
                'Project Type': item.get('project_type', {}).get('name', '') if item.get('project_type') else '',
                'Barangay': item.get('barangay', {}).get('name', '') if item.get('barangay') else '',
                'Municipality': item.get('municipality', {}).get('name', '') if item.get('municipality') else '',
                'Province': item.get('province', {}).get('name', '') if item.get('province') else '',
                'Latitude': item.get('latitude', ''),
                'Longitude': item.get('longitude', ''),
                'Activation Date': item.get('activation_date', ''),
                'Status': item.get('status', ''),
                'Remarks': item.get('remarks', ''),
                'Created At': item.get('created_at', ''),
                'Updated At': item.get('updated_at', ''),
            })

        df = pd.DataFrame(rows)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Projects')
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="projects_export.xlsx"'
        return response

    @action(detail=False, methods=['get'])
    def template(self, request):
        """Download CSV template for project import."""
        return self._get_template()

    def _get_template(self):
        """Get CSV template for project import."""
        # Define template headers
        headers = [
            'site_code', 'site_name', 'project_type_code', 'barangay_name',
            'municipality_name', 'province_name', 'latitude', 'longitude',
            'activation_date', 'status', 'remarks'
        ]

        # Create CSV with example data
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()

        # Add example row
        example = {
            'site_code': 'PRJ-001',
            'site_name': 'Example Project Site',
            'project_type_code': 'WATER',  # Must match existing project type code_prefix
            'barangay_name': 'Poblacion',  # Must match existing barangay name
            'municipality_name': 'Example Municipality',  # Must match existing municipality name
            'province_name': 'Example Province',  # Must match existing province name
            'latitude': '14.5995',
            'longitude': '120.9842',
            'activation_date': '2024-01-15',
            'status': 'pending',
            'remarks': 'Sample remarks'
        }
        writer.writerow(example)

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="project_import_template.csv"'
        return response
