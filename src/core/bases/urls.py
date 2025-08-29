from django.urls import path

from core.bases.views import BasePageView


app_name = "bases"

urlpatterns = [
    path("", BasePageView.as_view(), name='list')
]