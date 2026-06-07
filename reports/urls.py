from django.urls import path

from .views import DailyReportView


urlpatterns = [
    path("daily/", DailyReportView.as_view(), name="daily-report"),
]
