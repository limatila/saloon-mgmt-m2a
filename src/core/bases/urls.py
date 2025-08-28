from django.urls import path

from core.bases.views import BaseView


urlpatterns = [
    path("base", BaseView.as_view(), name='base-view')
]