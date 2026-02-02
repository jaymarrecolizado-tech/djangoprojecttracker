"""
Location models for the Project Tracking Management System.

This module provides models for the administrative hierarchy in the Philippines:
Province -> District -> Municipality -> Barangay

Each model includes spatial fields for geographic operations.
"""

from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _


class Province(models.Model):
    """
    Philippine Province model with spatial fields.

    Provinces are the primary administrative divisions in the Philippines.

    Attributes:
        name: Province name
        code: PSGC (Philippine Standard Geographic Code)
        centroid: Geographic center point
        boundary: Polygon boundary of the province
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Province name')
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text=_('PSGC code')
    )
    centroid = gis_models.PointField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
        help_text=_('Geographic center of the province')
    )
    boundary = gis_models.PolygonField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
        help_text=_('Boundary polygon of the province')
    )

    class Meta:
        """Meta options for Province model."""
        verbose_name = _('province')
        verbose_name_plural = _('provinces')
        ordering = ['name']
        db_table = 'locations_province'

    def __str__(self) -> str:
        """Return string representation of the province."""
        return self.name

    @property
    def district_count(self) -> int:
        """Get the number of districts in this province."""
        return self.districts.count()

    @property
    def municipality_count(self) -> int:
        """Get the number of municipalities in this province."""
        return self.municipalities.count()

    @property
    def barangay_count(self) -> int:
        """Get the number of barangays in this province."""
        return Barangay.objects.filter(municipality__province=self).count()


class District(models.Model):
    """
    Philippine District model with spatial fields.

    Districts are legislative districts within provinces.
    Not all provinces have districts (some use at-large representation).

    Attributes:
        name: District name
        code: District code
        province: Parent province
        centroid: Geographic center point
        boundary: Polygon boundary of the district
    """

    name = models.CharField(
        max_length=100,
        help_text=_('District name')
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text=_('District code')
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='districts',
        help_text=_('Parent province')
    )
    centroid = gis_models.PointField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
        help_text=_('Geographic center of the district')
    )
    boundary = gis_models.PolygonField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
        help_text=_('Boundary polygon of the district')
    )

    class Meta:
        """Meta options for District model."""
        verbose_name = _('district')
        verbose_name_plural = _('districts')
        ordering = ['province__name', 'name']
        db_table = 'locations_district'

    def __str__(self) -> str:
        """Return string representation of the district."""
        return f"{self.name}, {self.province.name}"

    @property
    def municipality_count(self) -> int:
        """Get the number of municipalities in this district."""
        return self.municipalities.count()


class Municipality(models.Model):
    """
    Philippine Municipality/City model with spatial fields.

    Municipalities are local government units within provinces.

    Attributes:
        name: Municipality name
        code: PSGC code
        province: Parent province
        district: Parent district (optional)
        is_city: Whether this is a city (True) or municipality (False)
        centroid: Geographic center point
        boundary: Polygon boundary of the municipality
    """

    name = models.CharField(
        max_length=100,
        help_text=_('Municipality/City name')
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text=_('PSGC code')
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='municipalities',
        help_text=_('Parent province')
    )
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        related_name='municipalities',
        null=True,
        blank=True,
        help_text=_('Parent district (optional)')
    )
    is_city = models.BooleanField(
        default=False,
        help_text=_('Whether this is a city')
    )
    city_class = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('City classification (e.g., Highly Urbanized City, Component City)')
    )
    centroid = gis_models.PointField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
        help_text=_('Geographic center of the municipality')
    )
    boundary = gis_models.PolygonField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
        help_text=_('Boundary polygon of the municipality')
    )

    class Meta:
        """Meta options for Municipality model."""
        verbose_name = _('municipality')
        verbose_name_plural = _('municipalities')
        ordering = ['province__name', 'name']
        db_table = 'locations_municipality'

    def __str__(self) -> str:
        """Return string representation of the municipality."""
        city_suffix = ' City' if self.is_city else ''
        return f"{self.name}{city_suffix}, {self.province.name}"

    @property
    def barangay_count(self) -> int:
        """Get the number of barangays in this municipality."""
        return self.barangays.count()

    @property
    def full_name(self) -> str:
        """Get the full name including city suffix."""
        city_suffix = ' City' if self.is_city else ''
        return f"{self.name}{city_suffix}"


class Barangay(models.Model):
    """
    Philippine Barangay model with spatial fields.

    Barangays are the smallest administrative divisions in the Philippines.

    Attributes:
        name: Barangay name
        code: PSGC code
        municipality: Parent municipality
        centroid: Geographic center point
        boundary: Polygon boundary of the barangay
    """

    name = models.CharField(
        max_length=100,
        help_text=_('Barangay name')
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text=_('PSGC code')
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='barangays',
        help_text=_('Parent municipality')
    )
    urban_rural = models.CharField(
        max_length=10,
        choices=[
            ('urban', _('Urban')),
            ('rural', _('Rural')),
        ],
        blank=True,
        help_text=_('Urban or rural classification')
    )
    centroid = gis_models.PointField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
        help_text=_('Geographic center of the barangay')
    )
    boundary = gis_models.PolygonField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
        help_text=_('Boundary polygon of the barangay')
    )

    class Meta:
        """Meta options for Barangay model."""
        verbose_name = _('barangay')
        verbose_name_plural = _('barangays')
        ordering = ['municipality__province__name', 'municipality__name', 'name']
        db_table = 'locations_barangay'

    def __str__(self) -> str:
        """Return string representation of the barangay."""
        return f"{self.name}, {self.municipality}"

    @property
    def full_address(self) -> str:
        """Get the full address including all parent locations."""
        return f"{self.name}, {self.municipality}, {self.municipality.province.name}"
