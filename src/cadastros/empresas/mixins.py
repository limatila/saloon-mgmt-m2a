from django.http import HttpResponseServerError

from cadastros.empresas.models import Empresa


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
