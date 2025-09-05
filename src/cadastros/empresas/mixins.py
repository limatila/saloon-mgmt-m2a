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
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(empresa=self.request.empresa)
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
