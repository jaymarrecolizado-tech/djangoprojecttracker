"""
Custom pagination classes for the Project Tracking Management System API.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class for API responses.

    Provides configurable page size with upper and lower bounds.
    Clients can specify page size using the 'page_size' query parameter.

    Query Parameters:
        page: Page number (1-indexed)
        page_size: Number of items per page (default: 50, max: 200)

    Example:
        GET /api/v1/projects/?page=2&page_size=25
    """

    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        Return a paginated response with additional metadata.

        Args:
            data: The paginated data to return

        Returns:
            Response with pagination metadata
        """
        return Response({
            'success': True,
            'data': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                    'page': self.page.number,
                    'pages': self.page.paginator.num_pages,
                    'page_size': self.get_page_size(self.request),
                }
            }
        })


class SmallResultsSetPagination(PageNumberPagination):
    """
    Small pagination class for limited result sets.

    Useful for dropdown lists and other UI elements that don't need
    large result sets.

    Query Parameters:
        page: Page number (1-indexed)
        page_size: Number of items per page (default: 10, max: 50)

    Example:
        GET /api/v1/project-types/?page_size=20
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        Return a paginated response with additional metadata.

        Args:
            data: The paginated data to return

        Returns:
            Response with pagination metadata
        """
        return Response({
            'success': True,
            'data': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                    'page': self.page.number,
                    'pages': self.page.paginator.num_pages,
                    'page_size': self.get_page_size(self.request),
                }
            }
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    Large pagination class for bulk operations.

    Useful for exports and bulk operations that need to process
    many records at once.

    Query Parameters:
        page: Page number (1-indexed)
        page_size: Number of items per page (default: 100, max: 500)

    Example:
        GET /api/v1/projects/?page_size=500
    """

    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        Return a paginated response with additional metadata.

        Args:
            data: The paginated data to return

        Returns:
            Response with pagination metadata
        """
        return Response({
            'success': True,
            'data': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                    'page': self.page.number,
                    'pages': self.page.paginator.num_pages,
                    'page_size': self.get_page_size(self.request),
                }
            }
        })


class NoPagination(PageNumberPagination):
    """
    No pagination class for returning all results.

    Warning: Use with caution on large datasets as this can
    significantly impact performance.

    Example:
        GET /api/v1/provinces/
    """

    page_size = None

    def paginate_queryset(self, queryset, request, view=None):
        """Return the full queryset without pagination."""
        return list(queryset)

    def get_paginated_response(self, data):
        """
        Return a response without pagination metadata.

        Args:
            data: The full data to return

        Returns:
            Response with data only
        """
        return Response({
            'success': True,
            'data': {
                'results': data,
                'pagination': None
            }
        })
