from django.urls import path

from servicos.agendamentos.views import (
    AgendamentoListView, AgendamentoCreateView, 
    AtualizarOuAvancarStatusFluxoAgendamentoView, VoltarStatusFluxoAgendamentoView, FinalizarAgendamentoView, 
    AgendamentoDeleteView,
    PlanilhaDiariaView
)

app_name = "agendamentos"

urlpatterns = [
    path('', AgendamentoListView.as_view(), name="list"), # type: ignore
    path("novo/", AgendamentoCreateView.as_view(), name="create"), # type: ignore
    path("next-status/<int:pk>/", AtualizarOuAvancarStatusFluxoAgendamentoView.as_view(), name="next-status"), # type: ignore
    path("last-status/<int:pk>/", VoltarStatusFluxoAgendamentoView.as_view(), name="last-status"), # type: ignore
    path("finalizar/", FinalizarAgendamentoView.as_view(), name="finalizar"), # type: ignore
    path("deletar/<int:pk>/", AgendamentoDeleteView.as_view(), name="delete"), # type: ignore
    path("planilha_diaria/<negint:data_difference>/", PlanilhaDiariaView.as_view(), name="planilha_diaria") # type: ignore
]
