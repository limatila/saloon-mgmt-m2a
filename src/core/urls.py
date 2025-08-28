from django.urls import path, include


app_name = "bases"

urlpatterns = [
    path("bases/", include('core.bases.urls', namespace="bases"))
]
