from django.urls import path
from .views import LoginView, LogoutView, MeView, csrf

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("me/", MeView.as_view()),
    path("csrf/", csrf, name="csrf"),
]
