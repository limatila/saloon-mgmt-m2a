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

        data_inicio, data_fim = self.get_query_range_dates()
        if data_inicio:
            queryset = queryset.filter(
                data_agendado__gte=data_inicio
            )
        if data_fim:
            queryset = queryset.filter(
                data_agendado__lte=data_fim
            )

        #optimizing
        queryset = queryset.select_related('cliente', 'servico', 'trabalhador')

        return queryset