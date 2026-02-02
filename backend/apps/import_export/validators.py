"""Validators for import_export app."""
import csv
import re
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.projects.models import ProjectType, ProjectSite, ProjectStatus
from apps.locations.models import Province, Municipality, Barangay


class CSVValidator:
    """Validator for CSV imports."""
    
    REQUIRED_FIELDS = ['site_code', 'site_name', 'project_type_code', 
                       'barangay_name', 'municipality_name', 'province_name',
                       'latitude', 'longitude', 'activation_date']
    
    OPTIONAL_FIELDS = ['status', 'remarks']
    
    VALID_STATUSES = [choice[0] for choice in ProjectStatus.choices]
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
        self.valid_rows = []
        self.invalid_rows = []
    
    def validate(self):
        """Validate the CSV file."""
        self.errors = []
        self.warnings = []
        self.valid_rows = []
        self.invalid_rows = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                # Read and validate headers
                sample = f.read(1024)
                f.seek(0)
                
                if not sample.strip():
                    raise ValidationError("CSV file is empty")
                
                # Parse headers
                header_line = sample.split('\n')[0]
                headers = self._parse_csv_line(header_line)
                headers = [h.strip().lower().replace(' ', '_') for h in headers]
                
                # Check required fields
                missing_fields = set(self.REQUIRED_FIELDS) - set(headers)
                if missing_fields:
                    raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
                
                # Read and validate each row
                reader = csv.DictReader(f, fieldnames=headers)
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (1-indexed + header)
                    row_errors = self._validate_row(row, row_num, headers)
                    if row_errors:
                        self.invalid_rows.append({
                            'row': row_num,
                            'errors': row_errors,
                            'data': dict(row)
                        })
                    else:
                        self.valid_rows.append(dict(row))
                
        except UnicodeDecodeError:
            raise ValidationError("CSV file must be UTF-8 encoded")
        except FileNotFoundError:
            raise ValidationError(f"File not found: {self.file_path}")
        
        return len(self.errors) == 0
    
    def _parse_csv_line(self, line):
        """Parse a CSV line, handling quoted values."""
        values = []
        current_value = ''
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                values.append(current_value.strip())
                current_value = ''
            else:
                current_value += char
        
        values.append(current_value.strip())
        return values
    
    def _validate_row(self, row, row_num, headers):
        """Validate a single row."""
        errors = []
        
        # Check required fields have values
        for field in self.REQUIRED_FIELDS:
            value = row.get(field, '').strip()
            if not value:
                errors.append(f"Required field '{field}' is empty")
        
        if errors:
            return errors
        
        # Validate specific fields
        site_code = row.get('site_code', '').strip()
        if self._exists(ProjectSite, 'site_code', site_code):
            errors.append(f"Project with site_code '{site_code}' already exists")
        
        project_type_code = row.get('project_type_code', '').strip()
        if not self._exists(ProjectType, 'code_prefix', project_type_code):
            errors.append(f"Invalid project_type_code '{project_type_code}' - must match existing project type")
        
        # Validate location fields
        barangay_name = row.get('barangay_name', '').strip()
        municipality_name = row.get('municipality_name', '').strip()
        province_name = row.get('province_name', '').strip()
        
        if not self._validate_location(barangay_name, municipality_name, province_name):
            errors.append(f"Invalid location combination: barangay='{barangay_name}', municipality='{municipality_name}', province='{province_name}'")
        
        # Validate coordinates
        try:
            latitude = float(row.get('latitude', '').strip())
            longitude = float(row.get('longitude', '').strip())
            if not -90 <= latitude <= 90:
                errors.append(f"Latitude must be between -90 and 90, got {latitude}")
            if not -180 <= longitude <= 180:
                errors.append(f"Longitude must be between -180 and 180, got {longitude}")
        except ValueError:
            errors.append("Latitude and longitude must be valid numbers")
        
        # Validate activation date
        activation_date = row.get('activation_date', '').strip()
        try:
            from datetime import datetime
            datetime.strptime(activation_date, '%Y-%m-%d')
        except ValueError:
            errors.append(f"Invalid activation_date '{activation_date}' - must be YYYY-MM-DD format")
        
        # Validate status if provided
        status = row.get('status', '').strip().lower()
        if status and status not in self.VALID_STATUSES:
            errors.append(f"Invalid status '{status}' - must be one of: {', '.join(self.VALID_STATUSES)}")
        
        return errors
    
    def _exists(self, model, field, value):
        """Check if a value exists in the database."""
        kwargs = {field: value}
        return model.objects.filter(**kwargs).exists()
    
    def _validate_location(self, barangay_name, municipality_name, province_name):
        """Validate that the location hierarchy exists."""
        try:
            province = Province.objects.get(name=province_name)
            municipality = Municipality.objects.get(name=municipality_name, province=province)
            barangay = Barangay.objects.get(name=barangay_name, municipality=municipality)
            return True
        except (Province.DoesNotExist, Municipality.DoesNotExist, Barangay.DoesNotExist):
            return False
    
    def get_summary(self):
        """Get validation summary."""
        return {
            'total_rows': len(self.valid_rows) + len(self.invalid_rows),
            'valid_rows': len(self.valid_rows),
            'invalid_rows': len(self.invalid_rows),
            'errors': self.errors,
            'warnings': self.warnings
        }


class DataTypeValidator:
    """Validator for data types in CSV."""
    
    @staticmethod
    def validate_integer(value, field_name, allow_negative=False):
        """Validate integer value."""
        try:
            int_value = int(value)
            if not allow_negative and int_value < 0:
                raise ValidationError(f"{field_name} must be a positive integer")
            return int_value
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer")
    
    @staticmethod
    def validate_decimal(value, field_name, min_value=None, max_value=None):
        """Validate decimal value."""
        try:
            decimal_value = float(value)
            if min_value is not None and decimal_value < min_value:
                raise ValidationError(f"{field_name} must be at least {min_value}")
            if max_value is not None and decimal_value > max_value:
                raise ValidationError(f"{field_name} must be at most {max_value}")
            return decimal_value
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number")
    
    @staticmethod
    def validate_date(value, field_name, date_format='%Y-%m-%d'):
        """Validate date value."""
        from datetime import datetime
        try:
            return datetime.strptime(value, date_format).date()
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be in {date_format} format")
    
    @staticmethod
    def validate_email(value, field_name):
        """Validate email value."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError(f"{field_name} must be a valid email address")
        return value
    
    @staticmethod
    def validate_max_length(value, field_name, max_length):
        """Validate maximum string length."""
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must be at most {max_length} characters")
        return value


class ForeignKeyValidator:
    """Validator for foreign key relationships."""
    
    @staticmethod
    def validate_fk(model, value, field_name):
        """Validate foreign key exists."""
        if not model.objects.filter(id=value).exists():
            raise ValidationError(f"{field_name} with id {value} does not exist")
        return model.objects.get(id=value)
    
    @staticmethod
    def validate_fk_by_field(model, field, value, field_name):
        """Validate foreign key exists by custom field."""
        kwargs = {field: value}
        if not model.objects.filter(**kwargs).exists():
            raise ValidationError(f"{field_name} '{value}' does not exist")
        return model.objects.get(**kwargs)
