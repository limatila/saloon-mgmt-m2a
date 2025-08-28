from django.urls import path, include


urlpatterns = [
    path("bases/", include('core.bases.urls'), name="bases")
]
