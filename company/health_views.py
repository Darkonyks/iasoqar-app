"""
Health check views for monitoring and deployment verification
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import sys


def health_check(request):
    """
    Simple health check endpoint that verifies:
    - Application is running
    - Database connection is working
    - Basic system info
    """
    health_status = {
        "status": "healthy",
        "application": "ISOQAR",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "django_version": settings.VERSION if hasattr(settings, 'VERSION') else "unknown",
        "debug_mode": settings.DEBUG,
    }
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"
        return JsonResponse(health_status, status=503)
    
    return JsonResponse(health_status, status=200)


def readiness_check(request):
    """
    Readiness check - verifies if the application is ready to serve traffic
    """
    ready_status = {
        "ready": True,
        "checks": {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
            ready_status["checks"]["database"] = {
                "status": "ready",
                "migrations_applied": migration_count
            }
    except Exception as e:
        ready_status["ready"] = False
        ready_status["checks"]["database"] = {
            "status": "not_ready",
            "error": str(e)
        }
    
    status_code = 200 if ready_status["ready"] else 503
    return JsonResponse(ready_status, status=status_code)


def liveness_check(request):
    """
    Liveness check - simple check that the application is alive
    """
    return JsonResponse({"alive": True}, status=200)
