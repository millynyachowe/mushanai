"""
Custom Error Handlers for Mushanai
Provides custom error pages and Sentry integration
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import sentry_sdk


def handler404(request, exception):
    """
    Custom 404 error handler
    """
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
            'status': 404
        }, status=404)
    
    context = {
        'error_code': '404',
        'error_title': 'Page Not Found',
        'error_message': 'The page you are looking for does not exist.',
    }
    return render(request, 'errors/404.html', context, status=404)


def handler500(request):
    """
    Custom 500 error handler
    """
    # Capture exception in Sentry
    if hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
        sentry_sdk.capture_exception()
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Our team has been notified.',
            'status': 500
        }, status=500)
    
    context = {
        'error_code': '500',
        'error_title': 'Server Error',
        'error_message': 'Something went wrong on our end. We\'ve been notified and are working on it.',
    }
    return render(request, 'errors/500.html', context, status=500)


def handler403(request, exception):
    """
    Custom 403 error handler
    """
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.',
            'status': 403
        }, status=403)
    
    context = {
        'error_code': '403',
        'error_title': 'Access Denied',
        'error_message': 'You do not have permission to view this page.',
    }
    return render(request, 'errors/403.html', context, status=403)


def handler400(request, exception):
    """
    Custom 400 error handler
    """
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Bad Request',
            'message': 'The request could not be understood or was missing required parameters.',
            'status': 400
        }, status=400)
    
    context = {
        'error_code': '400',
        'error_title': 'Bad Request',
        'error_message': 'Your request could not be processed.',
    }
    return render(request, 'errors/400.html', context, status=400)

