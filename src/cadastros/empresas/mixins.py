from django.db.models import Q, Model, ForeignKey
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseServerError

from cadastros.empresas.models import Empresa


class ContextoEmpresaMixin:
    """
    Adiciona self.empresa à viewm baseado em 'empresa_id' presente na session do Django.
    Ou se não existe empresa_id, volta pra página de seleção de empresa
    """
    def dispatch(self, request, *args, **kwargs):
        empresa_id = request.session.get("empresa_id", None)

        if not empresa_id:
            return redirect('cadastros:empresas:select')

        self.request.empresa = get_object_or_404(Empresa, id=empresa_id, user_id=request.user.id)
        return super().dispatch(request, *args, **kwargs)


class EscopoEmpresaQuerysetMixin(ContextoEmpresaMixin):
    """
    Filtra toda a queryset para mostrar a empresa registrada da request
    """
    @property
    def empresa_filter(self):
        return Q(empresa=self.request.empresa)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(self.empresa_filter)
        return queryset


class EscopoEmpresaFormMixin(ContextoEmpresaMixin):
    """
    Adiciona a empresa relacionada ao formulário, baseado na empresa registrada da request
    """
    def form_valid(self, form):
        form.instance.empresa = self.request.empresa
        return super().form_valid(form)


class EmpresaDoUserQuerysetMixin:
    """
    Filtra todas as empresas baseado no usuário logado.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.model is not Empresa:
            raise HttpResponseServerError(f"Erro na view {self.__name__}, model não foi definido para \'Empresa\'")

        queryset = queryset.filter(user=self.request.user)
        return queryset


class FormFieldsComEscopoEmpresaMixin(EscopoEmpresaFormMixin):
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
