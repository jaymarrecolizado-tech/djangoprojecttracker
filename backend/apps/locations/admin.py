"""
Admin configuration for the locations app.

This module customizes the Django admin interface for location management.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Province, District, Municipality, Barangay


class MunicipalityInline(admin.TabularInline):
    """Inline admin for municipalities within a province."""
    model = Municipality
    extra = 0
    fields = ['name', 'code', 'is_city']
    show_change_link = True


class BarangayInline(admin.TabularInline):
    """Inline admin for barangays within a municipality."""
    model = Barangay
    extra = 0
    fields = ['name', 'code', 'urban_rural']
    show_change_link = True


@admin.register(Province)
class ProvinceAdmin(admin.GISModelAdmin):
    """
    Admin configuration for Province model.

    Provides GIS-enabled admin interface for managing provinces.
    """

    list_display = [
        'name',
        'code',
        'municipality_count',
        'district_count',
        'barangay_count',
    ]
    list_filter = []
    search_fields = ['name', 'code']
    ordering = ['name']
    inlines = [MunicipalityInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'code')
        }),
        (_('Spatial Data'), {
            'fields': ('centroid', 'boundary'),
            'classes': ('collapse',)
        }),
    )

    def municipality_count(self, obj: Province) -> int:
        """Get the number of municipalities in the province."""
        return obj.municipalities.count()
    municipality_count.short_description = _('Municipalities')

    def district_count(self, obj: Province) -> int:
        """Get the number of districts in the province."""
        return obj.districts.count()
    district_count.short_description = _('Districts')

    def barangay_count(self, obj: Province) -> int:
        """Get the number of barangays in the province."""
        return Barangay.objects.filter(municipality__province=obj).count()
    barangay_count.short_description = _('Barangays')


@admin.register(District)
class DistrictAdmin(admin.GISModelAdmin):
    """
    Admin configuration for District model.

    Provides GIS-enabled admin interface for managing districts.
    """

    list_display = [
        'name',
        'code',
        'province',
        'municipality_count',
    ]
    list_filter = ['province']
    search_fields = ['name', 'code', 'province__name']
    ordering = ['province__name', 'name']

    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'province')
        }),
        (_('Spatial Data'), {
            'fields': ('centroid', 'boundary'),
            'classes': ('collapse',)
        }),
    )

    def municipality_count(self, obj: District) -> int:
        """Get the number of municipalities in the district."""
        return obj.municipalities.count()
    municipality_count.short_description = _('Municipalities')


@admin.register(Municipality)
class MunicipalityAdmin(admin.GISModelAdmin):
    """
    Admin configuration for Municipality model.

    Provides GIS-enabled admin interface for managing municipalities.
    """

    list_display = [
        'name',
        'code',
        'province',
        'district',
        'is_city',
        'barangay_count',
    ]
    list_filter = [
        'province',
        'is_city',
        'city_class',
    ]
    search_fields = ['name', 'code', 'province__name']
    ordering = ['province__name', 'name']
    inlines = [BarangayInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'province', 'district')
        }),
        (_('Classification'), {
            'fields': ('is_city', 'city_class')
        }),
        (_('Spatial Data'), {
            'fields': ('centroid', 'boundary'),
            'classes': ('collapse',)
        }),
    )

    def barangay_count(self, obj: Municipality) -> int:
        """Get the number of barangays in the municipality."""
        return obj.barangays.count()
    barangay_count.short_description = _('Barangays')


@admin.register(Barangay)
class BarangayAdmin(admin.GISModelAdmin):
    """
    Admin configuration for Barangay model.

    Provides GIS-enabled admin interface for managing barangays.
    """

    list_display = [
        'name',
        'code',
        'municipality',
        'province_name',
        'urban_rural',
    ]
    list_filter = [
        'municipality__province',
        'urban_rural',
    ]
    search_fields = [
        'name',
        'code',
        'municipality__name',
        'municipality__province__name'
    ]
    ordering = ['municipality__province__name', 'municipality__name', 'name']

    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'municipality', 'urban_rural')
        }),
        (_('Spatial Data'), {
            'fields': ('centroid', 'boundary'),
            'classes': ('collapse',)
        }),
    )

    def province_name(self, obj: Barangay) -> str:
        """Get the province name for the barangay."""
        return obj.municipality.province.name
    province_name.short_description = _('Province')
    province_name.admin_order_field = 'municipality__province__name'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'municipality',
            'municipality__province'
        )
