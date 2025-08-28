from django.urls import path

from core.bases.views import BaseView


app_name = "bases"

urlpatterns = [
    path("", BaseView.as_view(), name='list')
]