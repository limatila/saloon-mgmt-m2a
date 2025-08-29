from django.urls import path, include

from servicos.agendamentos.views import AgendamentoListView


app_name = "agendamentos"

urlpatterns = [
    path('', AgendamentoListView.as_view(), name="list")
]
