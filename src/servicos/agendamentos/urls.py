from django.urls import path, include

from servicos.agendamentos.views import AgendamentoListView, AgendamentoCreateView, FinalizarAgendamentoView


app_name = "agendamentos"

urlpatterns = [
    path('', AgendamentoListView.as_view(), name="list"),
    path("novo/", AgendamentoCreateView.as_view(), name="create"),
    path("finalizar/", FinalizarAgendamentoView.as_view(), name="finalizar"),
]
