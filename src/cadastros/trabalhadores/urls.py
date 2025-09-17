from django.urls import path, include

from cadastros.trabalhadores.views import TrabalhadoresListView, TrabalhadorCreateView, TrabalhadorDeleteView


app_name = "trabalhadores"

urlpatterns = [
    path('', TrabalhadoresListView.as_view(), name="list"),
    path('novo/', TrabalhadorCreateView.as_view(), name="create"),
    path("deletar/<int:pk>/", TrabalhadorDeleteView.as_view(), name="delete")
]
