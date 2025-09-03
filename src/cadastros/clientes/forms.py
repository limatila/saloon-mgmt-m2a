from django import forms

from cadastros.clientes.models import Cliente
from core.pessoas.forms import BasePessoasForm


class ClientesForm(BasePessoasForm):
    class Meta:
        model = Cliente