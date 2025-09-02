from django.db.models import Count, Q

from core.pessoas.views import PessoasListView
from cadastros.trabalhadores.models import Trabalhador


class TrabalhadoresListView(PessoasListView):
    model = Trabalhador

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.annotate(
            agendamentos_totais=Count('agendamento'),
            agendamentos_pendentes=Count('agendamento', filter=Q(agendamento__status="PENDENTE"))
        )
        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Trabalhadores"
        return contexto
