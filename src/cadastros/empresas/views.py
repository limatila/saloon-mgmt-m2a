from django.db.models import Q, ForeignKey, Model
from django.db.models import ForeignKey, Model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseServerError
from django.contrib import messages

from core.bases.views import SelecaoDynamicListView, BaseDynamicFormView
from cadastros.empresas.mixins import EscopoEmpresaFormMixin
from cadastros.empresas.models import Empresa
from cadastros.empresas.mixins import EmpresaDoUserQuerysetMixin


class SelecaoEmpresasListView(LoginRequiredMixin, EmpresaDoUserQuerysetMixin, SelecaoDynamicListView):
    model = Empresa

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
        contexto['description'] = "O sistema irá mostrar as informações da sua empresa registrada e ativa no sistema."
        contexto['sidebar'] = False
        contexto['query'] = self.request.GET.get("query", "").strip()
        return contexto

    def post(self, request, *args, **kwargs):
        empresa_id = self.get_selecao_or_redirect(request)

        if not empresa_id:
            messages.warning(request, "⚠️ Você precisa selecionar uma empresa.")
            return redirect(request.path)  # back to the same page
        try:
            empresa = get_object_or_404(
            Empresa.objects.filter(user=request.user),  # garante que a empresa é do user
            id=empresa_id
        )
            request.session["empresa_id"] = empresa.id
        except Empresa.DoesNotExist:
            messages.error(request, "⚠️ Essa empresa não pode ser carregada.")     
        
        return redirect("home")
