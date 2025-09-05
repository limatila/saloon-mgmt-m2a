from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

from core.bases.views import DynamicListView
from cadastros.empresas.models import Empresa
from cadastros.empresas.mixins import EmpresaDoUserQuerysetMixin


class SelecaoEmpresasListView(EmpresaDoUserQuerysetMixin, DynamicListView):
    model = Empresa
    # baseado_em_empresa = False #não executa mixin atribuindo empresa à request

    def get_fields_display(self):
        return ['nome_fantasia', 'razao_social', 'cnpj']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("query", "").strip()

        if query:
            condicao_cnpj = Q(cnpj__exact=query)
            condicao_fantasia = Q(nome_fantasia__icontains=query)
            condicao_razao = Q(razao_social__icontains=query)

            queryset = queryset.filter(
                condicao_cnpj | condicao_fantasia | condicao_razao
            )

        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Selecione sua empresa"
        contexto['description'] = "O aplicativo irá mostrar as informações da sua empresa registrada e ativa no sistema."
        contexto['sidebar'] = False
        contexto['query'] = self.request.GET.get("query", "")
        return contexto


    def post(self, request, *args, **kwargs):
        empresa_id = request.POST.get("empresa_id")
        if not empresa_id:
            return redirect("cadastros:empresas:select")

        empresa = get_object_or_404(
            Empresa.objects.filter(user=request.user),  # garante que a empresa é do user
            id=empresa_id
        )
        request.session["empresa_id"] = empresa.id
        return redirect("home")
