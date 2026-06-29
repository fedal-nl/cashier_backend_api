from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch


class HealthViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint_returns_ok(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": 200, "database": "ok"})

    def test_health_live_endpoint_returns_ok(self):
        response = self.client.get("/health/live/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": 200})

    @patch("config.views.connection.cursor")
    def test_health_endpoint_returns_unavailable_when_database_check_fails(
        self, cursor
    ):
        cursor.side_effect = Exception("database unavailable")

        with self.assertLogs("config.views", level="ERROR"):
            response = self.client.get("/health/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "status": 503,
                "database": "unavailable",
            },
        )
