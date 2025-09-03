from django import forms

from cadastros.trabalhadores.models import Trabalhador
from core.pessoas.forms import BasePessoasForm


class TrabalhadoresForm(BasePessoasForm):
    class Meta:
        model = Trabalhador