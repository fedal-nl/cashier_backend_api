import logging
import os

from django.db import connection
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


@extend_schema(exclude=True)
def health_live(request):
    logger.info(
        "health_live check served by %s",
        os.environ.get("BACKEND_INSTANCE", "unknown"),
    )
    return JsonResponse({"status": 200})


@extend_schema(exclude=True)
def health(request):
    backend_instance = os.environ.get("BACKEND_INSTANCE", "unknown")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        logger.exception("health check failed on %s", backend_instance)
        return JsonResponse(
            {
                "status": 503,
                "database": "unavailable",
            },
            status=503,
        )

    logger.info("health check served by %s", backend_instance)
    return JsonResponse(
        {
            "status": 200,
            "database": "ok",
        }
    )
