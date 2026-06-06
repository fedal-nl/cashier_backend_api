from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


class AuthenticationViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="cashier",
            password="test1234"
        )

    def test_login_success(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "cashier",
                "password": "test1234"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.json()["message"],
            "Logged in"
        )

    def test_login_invalid_credentials(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "cashier",
                "password": "wrong"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            401
        )

        self.assertEqual(
            response.json()["error"],
            "Invalid credentials"
        )

    def test_me_authenticated(self):
        self.client.login(
            username="cashier",
            password="test1234"
        )

        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertTrue(
            response.json()["authenticated"]
        )

        self.assertEqual(
            response.json()["username"],
            "cashier"
        )

    def test_me_unauthenticated(self):
        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.json(),
            {"authenticated": False}
        )

    def test_csrf_returns_token(self):
        response = self.client.get(
            "/api/auth/csrf/"
        )

        data = response.json()

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            "csrfToken",
            data
        )

        self.assertTrue(
            data["csrfToken"]
        )

    def test_logout(self):
        self.client.login(
            username="cashier",
            password="test1234"
        )

        response = self.client.post(
            "/api/auth/logout/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.json()["message"],
            "Logged out"
        )

        me_response = self.client.get(
            "/api/auth/me/"
        )

        self.assertFalse(
            me_response.json()["authenticated"]
        )

    def test_logout_without_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(
            username="cashier",
            password="test1234"
        )

        response = client.post(
            "/api/auth/logout/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.json()["message"],
            "Logged out"
        )

        me_response = client.get(
            "/api/auth/me/"
        )

        self.assertFalse(
            me_response.json()["authenticated"]
        )
