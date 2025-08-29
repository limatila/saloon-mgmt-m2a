from django.urls import path, include

from cadastros.trabalhadores.views import TrabalhadoresListView


app_name = "trabalhadores"

urlpatterns = [
    path('', TrabalhadoresListView.as_view(), name="list")
]
