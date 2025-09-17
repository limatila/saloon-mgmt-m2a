from django.urls import path

from .views import ClientesListView, ClienteCreateView, ClienteDeleteView


app_name = "clientes"

urlpatterns = [
    path('', ClientesListView.as_view(), name='list'),
    path("novo/", ClienteCreateView.as_view(), name="create"),
    path("deletar/<int:pk>/", ClienteDeleteView.as_view(), name="delete")
]