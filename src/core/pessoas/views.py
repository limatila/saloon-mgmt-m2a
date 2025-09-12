from django.views.generic import CreateView
from django.db.models import Q

from core.bases.views import BaseDynamicListView, BaseDynamicFormView
from core.bases.mixins import FormComArquivoMixin


class PessoasListView(BaseDynamicListView):
    def get_fields_display(self):
        return ['nome', 'cpf', 'imagem', 'telefone', 'endereco']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("query", "").strip()

        if query:
            condicao_nome = Q(nome__icontains=query)
            condicao_cpf = Q(cpf__icontains=query.replace('.', '').replace('-', ''))
            condicao_telefone = Q(telefone__icontains=query.replace('(', '').replace(')', '').replace('-', ''))
            condicao_endereco = Q(endereco__icontains=query)

            queryset = queryset.filter(
                condicao_nome | condicao_cpf | condicao_telefone | condicao_endereco
            )

        return queryset


class PessoasCreateView(FormComArquivoMixin, BaseDynamicFormView, CreateView):
    pass
