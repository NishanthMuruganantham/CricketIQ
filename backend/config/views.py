from django.http import JsonResponse
from django.utils import timezone


def api_root(request):
    """
    API Root / Homepage
    Provides metadata about the CricketIQ API.
    """
    return JsonResponse({
        "name": "CricketIQ API",
        "version": "1.0.0",
        "description": "AI-powered cricket analytics API for Men's T20I data.",
        "documentation": "https://github.com/NishanthMuruganantham/CricketIQ",
        "status": "running",
        "timestamp": timezone.now().isoformat(),
        "endpoints": {
            "chat": "/api/chat/ask/",
            "health": "/health/"
        }
    })


def health_check(request):
    """
    Health Check Endpoint
    Returns 200 OK if the service is up.
    """
    return JsonResponse({
        "status": "ok",
        "timestamp": timezone.now().isoformat()
    })
