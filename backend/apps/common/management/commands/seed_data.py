"""Management command to seed reference data."""
from django.core.management.base import BaseCommand
from apps.projects.models import ProjectType
from apps.accounts.models import User, UserRole

class Command(BaseCommand):
    """Seed reference data for the application."""
    help = 'Seed reference data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create project types
        project_types = [
            {'name': 'Water System', 'code_prefix': 'WS', 'color_code': '#3B82F6'},
            {'name': 'Road Construction', 'code_prefix': 'RC', 'color_code': '#10B981'},
            {'name': 'School Building', 'code_prefix': 'SB', 'color_code': '#F59E0B'},
            {'name': 'Health Center', 'code_prefix': 'HC', 'color_code': '#EF4444'},
        ]

        for pt in project_types:
            ProjectType.objects.get_or_create(
                code_prefix=pt['code_prefix'],
                defaults=pt
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(project_types)} project types'))

        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                full_name='Administrator',
                role=UserRole.ADMIN
            )
            self.stdout.write(self.style.SUCCESS('Created admin user (admin/admin123)'))

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
