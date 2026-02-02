"""Celery tasks for CSV import."""
import pandas as pd
from celery import shared_task
from django.utils import timezone
from apps.projects.models import ProjectSite, ProjectType, ProjectStatus
from apps.locations.models import Barangay
from .models import CSVImport, ImportStatus

@shared_task(bind=True)
def process_csv_import(self, import_id):
    """Process CSV import asynchronously."""
    try:
        csv_import = CSVImport.objects.get(id=import_id)
        csv_import.status = ImportStatus.PROCESSING
        csv_import.started_at = timezone.now()
        csv_import.save()

        errors = []
        success_count = 0

        # Read CSV
        df = pd.read_csv(csv_import.file_path)
        csv_import.total_rows = len(df)
        csv_import.save()

        for index, row in df.iterrows():
            try:
                # Get related objects
                project_type = ProjectType.objects.get(code_prefix=row.get('project_type'))
                barangay = Barangay.objects.get(code=row.get('barangay_code'))

                # Create project
                ProjectSite.objects.create(
                    site_code=row.get('site_code'),
                    site_name=row.get('site_name'),
                    project_type=project_type,
                    barangay=barangay,
                    municipality=barangay.municipality,
                    province=barangay.municipality.province,
                    latitude=row.get('latitude'),
                    longitude=row.get('longitude'),
                    activation_date=row.get('activation_date'),
                    status=row.get('status', ProjectStatus.PENDING),
                    remarks=row.get('remarks', ''),
                    created_by=csv_import.uploaded_by
                )
                success_count += 1
            except Exception as e:
                errors.append({'row': index + 1, 'error': str(e)})

        csv_import.success_count = success_count
        csv_import.error_count = len(errors)
        csv_import.errors = errors
        csv_import.status = ImportStatus.COMPLETED if len(errors) == 0 else ImportStatus.FAILED
        csv_import.completed_at = timezone.now()
        csv_import.save()

    except Exception as e:
        csv_import.status = ImportStatus.FAILED
        csv_import.errors = [{'error': str(e)}]
        csv_import.completed_at = timezone.now()
        csv_import.save()
