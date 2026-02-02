"""
Standardized API response utilities for the Project Tracking Management System.

This module provides consistent response formatting across all API endpoints,
ensuring a uniform structure for both successful responses and errors.
"""

from typing import Any, Dict, Optional, List
from rest_framework.response import Response
from rest_framework import status


def success_response(
    data: Any = None,
    message: str = 'Success',
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict] = None
) -> Response:
    """
    Create a standardized success response.

    Args:
        data: The response data payload
        message: Human-readable success message
        status_code: HTTP status code (default: 200)
        meta: Additional metadata to include in response

    Returns:
        DRF Response object with standardized format

    Example:
        >>> return success_response(
        ...     data={'id': 1, 'name': 'Project A'},
        ...     message='Project created successfully'
        ... )
    """
    response_data = {
        'success': True,
        'message': message,
        'data': data
    }

    if meta is not None:
        response_data['meta'] = meta

    return Response(response_data, status=status_code)


def error_response(
    message: str = 'An error occurred',
    errors: Optional[Dict] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_code: Optional[str] = None
) -> Response:
    """
    Create a standardized error response.

    Args:
        message: Human-readable error message
        errors: Detailed error information (field-level errors, etc.)
        status_code: HTTP status code (default: 400)
        error_code: Application-specific error code for client handling

    Returns:
        DRF Response object with standardized error format

    Example:
        >>> return error_response(
        ...     message='Validation failed',
        ...     errors={'name': ['This field is required']},
        ...     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ...     error_code='VALIDATION_ERROR'
        ... )
    """
    response_data = {
        'success': False,
        'message': message,
        'data': None
    }

    if errors is not None:
        response_data['errors'] = errors

    if error_code is not None:
        response_data['error_code'] = error_code

    return Response(response_data, status=status_code)


def created_response(
    data: Any,
    message: str = 'Resource created successfully'
) -> Response:
    """
    Create a standardized response for successful resource creation.

    Args:
        data: The created resource data
        message: Success message

    Returns:
        DRF Response with 201 status code
    """
    return success_response(
        data=data,
        message=message,
        status_code=status.HTTP_201_CREATED
    )


def deleted_response(
    message: str = 'Resource deleted successfully'
) -> Response:
    """
    Create a standardized response for successful deletion.

    Args:
        message: Success message

    Returns:
        DRF Response with 200 status code (or 204 if no content preferred)
    """
    return success_response(
        data=None,
        message=message,
        status_code=status.HTTP_200_OK
    )


def paginated_response(
    results: List[Any],
    count: int,
    page: int,
    pages: int,
    page_size: int,
    next_url: Optional[str] = None,
    previous_url: Optional[str] = None,
    message: str = 'Success'
) -> Response:
    """
    Create a standardized paginated response.

    Args:
        results: List of items for the current page
        count: Total number of items
        page: Current page number
        pages: Total number of pages
        page_size: Number of items per page
        next_url: URL for the next page (if available)
        previous_url: URL for the previous page (if available)
        message: Success message

    Returns:
        DRF Response with paginated data structure
    """
    return success_response(
        data={
            'results': results,
            'pagination': {
                'count': count,
                'page': page,
                'pages': pages,
                'page_size': page_size,
                'next': next_url,
                'previous': previous_url
            }
        },
        message=message
    )


def validation_error_response(
    errors: Dict,
    message: str = 'Validation failed'
) -> Response:
    """
    Create a standardized validation error response.

    Args:
        errors: Field-level validation errors
        message: General validation error message

    Returns:
        DRF Response with 422 status code
    """
    return error_response(
        message=message,
        errors=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code='VALIDATION_ERROR'
    )


def not_found_response(
    resource_name: str = 'Resource',
    resource_id: Optional[Any] = None
) -> Response:
    """
    Create a standardized not found error response.

    Args:
        resource_name: Name of the resource type
        resource_id: ID of the resource that was not found

    Returns:
        DRF Response with 404 status code
    """
    if resource_id is not None:
        message = f'{resource_name} with id {resource_id} not found'
    else:
        message = f'{resource_name} not found'

    return error_response(
        message=message,
        status_code=status.HTTP_404_NOT_FOUND,
        error_code='NOT_FOUND'
    )


def forbidden_response(
    message: str = 'You do not have permission to perform this action'
) -> Response:
    """
    Create a standardized forbidden error response.

    Args:
        message: Permission denied message

    Returns:
        DRF Response with 403 status code
    """
    return error_response(
        message=message,
        status_code=status.HTTP_403_FORBIDDEN,
        error_code='FORBIDDEN'
    )


def unauthorized_response(
    message: str = 'Authentication credentials were not provided'
) -> Response:
    """
    Create a standardized unauthorized error response.

    Args:
        message: Unauthorized message

    Returns:
        DRF Response with 401 status code
    """
    return error_response(
        message=message,
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_code='UNAUTHORIZED'
    )


def server_error_response(
    message: str = 'An internal server error occurred'
) -> Response:
    """
    Create a standardized server error response.

    Args:
        message: Error message

    Returns:
        DRF Response with 500 status code
    """
    return error_response(
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code='INTERNAL_ERROR'
    )


def conflict_response(
    message: str = 'Resource already exists',
    errors: Optional[Dict] = None
) -> Response:
    """
    Create a standardized conflict error response.

    Args:
        message: Conflict message
        errors: Detailed error information

    Returns:
        DRF Response with 409 status code
    """
    return error_response(
        message=message,
        errors=errors,
        status_code=status.HTTP_409_CONFLICT,
        error_code='CONFLICT'
    )
