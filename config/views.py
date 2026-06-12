from django.db import connection
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema


@extend_schema(exclude=True)
def health_live(request):
    return JsonResponse({"status": 200})


@extend_schema(exclude=True)
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse(
            {
                "status": 503,
                "database": "unavailable",
            },
            status=503,
        )

    return JsonResponse(
        {
            "status": 200,
            "database": "ok",
        }
    )
