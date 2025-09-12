from django import forms

from servicos.tipo_servicos.models import TipoServico


class TipoServicoForm(forms.ModelForm):
    class Meta:
        model = TipoServico
        fields = ['nome', 'preco']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-field', 'placeholder': "nome de nome"}),
            'CPF': forms.TextInput(attrs={'class': 'form-field', 'placeholder': "R$ XX.xx"}),
        }