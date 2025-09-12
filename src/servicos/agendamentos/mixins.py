from django.db.models import Q

class AgendamentosSearchMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("query", "").strip()

        if query:
            condicao_cliente = Q(cliente__nome__icontains=query)
            condicao_servico = Q(servico__nome__icontains=query)
            condicao_trabalhador = Q(trabalhador__nome__icontains=query)

            queryset = queryset.filter(
                condicao_cliente | condicao_servico | condicao_trabalhador
            )

        queryset = queryset.select_related('cliente', 'servico', 'trabalhador')

        return queryset