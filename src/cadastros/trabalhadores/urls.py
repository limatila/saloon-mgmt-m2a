from django.urls import path, include

from cadastros.trabalhadores.views import TrabalhadoresListView, TrabalhadorCreateView


app_name = "trabalhadores"

urlpatterns = [
    path('', TrabalhadoresListView.as_view(), name="list"),
    path('novo/', TrabalhadorCreateView.as_view(), name="create")
]
