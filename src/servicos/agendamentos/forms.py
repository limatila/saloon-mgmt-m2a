from django import forms

from servicos.agendamentos.models import Agendamento
from cadastros.clientes.models import Cliente
from cadastros.trabalhadores.models import Trabalhador
from cadastros.tipo_servicos.models import TipoServico


class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['data_agendado', 'status', 'cliente', 'servico', 'trabalhador']
        widgets = {
            'data_agendado': forms.DateTimeInput(attrs={'class': 'form-field', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-field'}),
            'cliente': forms.Select(attrs={'class': 'form-field'}),
            'servico': forms.Select(attrs={'class': 'form-field'}),
            'trabalhador': forms.Select(attrs={'class': 'form-field'})
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop("empresa", None)  # remove do kwargs antes do super() falhar
        
        super().__init__(*args, **kwargs)     
        
        if empresa:
            self.fields["cliente"].queryset = Cliente.objects.filter(empresa=empresa)
            self.fields["trabalhador"].queryset = Trabalhador.objects.filter(empresa=empresa)
            self.fields["servico"].queryset = TipoServico.objects.filter(empresa=empresa)
        else:
            raise Exception(f"Erro no form {self.__class__.__name__}, empresa não está na sessão.")
