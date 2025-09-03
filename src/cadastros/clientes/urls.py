from django.urls import path

from .views import ClientesListView, ClienteCreateView


app_name = "clientes"

urlpatterns = [
    path('', ClientesListView.as_view(), name='list'),
    path("novo/", ClienteCreateView.as_view(), name="create")
]