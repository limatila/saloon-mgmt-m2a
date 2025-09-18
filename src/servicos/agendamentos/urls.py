from django.urls import path, include

from servicos.agendamentos.views import AgendamentoListView, AgendamentoCreateView, AtualizarStatusFluxoAgendamentoView, FinalizarAgendamentoView, AgendamentoDeleteView, PlanilhaDiariaView


app_name = "agendamentos"

urlpatterns = [
    path('', AgendamentoListView.as_view(), name="list"),
    path("novo/", AgendamentoCreateView.as_view(), name="create"),
    path("next-status/<int:pk>/", AtualizarStatusFluxoAgendamentoView.as_view(), name="next-status"),
    path("finalizar/", FinalizarAgendamentoView.as_view(), name="finalizar"),
    path("deletar/<int:pk>/", AgendamentoDeleteView.as_view(), name="delete"),
    path("planilha_diaria/<negint:data_difference>/", PlanilhaDiariaView.as_view(), name="planilha_diaria")
]
