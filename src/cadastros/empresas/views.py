from django.db.models import Q, ForeignKey, Model
from django.db.models import ForeignKey, Model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseServerError

from core.bases.views import BaseDynamicListView, BaseDynamicFormView
from cadastros.empresas.mixins import EscopoEmpresaFormMixin
from cadastros.empresas.models import Empresa
from cadastros.empresas.mixins import EmpresaDoUserQuerysetMixin


class SelecaoEmpresasListView(LoginRequiredMixin, EmpresaDoUserQuerysetMixin, BaseDynamicListView):
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


class EscopoEmpresaFieldsFormView(LoginRequiredMixin, EscopoEmpresaFormMixin, BaseDynamicFormView):
    fields_ignorados = ['empresa', 'data_criado', 'data_modificado']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # injeta a empresa que o ContextoEmpresaMixin já colocou em request
        kwargs["empresa"] = self.request.empresa
        return kwargs

    def form_valid(self, form: ModelForm):
        for field in form._meta.model._meta.get_fields():
            if field in self.fields_ignorados: continue

            # se o valor do field não pertence a empresa logada na sessão
            if isinstance(field, ForeignKey):
                field_obj: Model = form.cleaned_data.get(field.name, None)
                if ((field_obj and hasattr(field_obj, "empresa")) and
                    (field_obj.empresa.id != self.request.empresa.id)):
                    raise HttpResponseServerError(f"Erro em {self.__class__.__name__}, field {field.verbose_name} não obteve valor válido para empresa em sessão.")

        return super().form_valid(form)