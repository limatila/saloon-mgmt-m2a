from django import forms

from servicos.agendamentos.models import Agendamento
from cadastros.clientes.models import Cliente
from cadastros.trabalhadores.models import Trabalhador
from servicos.tipo_servicos.models import TipoServico


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
        
        fields_models = {
            "cliente": Cliente,
            "servico": TipoServico,
            "trabalhador": Trabalhador
        }

        if empresa:
            for field in fields_models.keys():
                    self.fields[field].queryset = (
                        fields_models[field].objects.filter(
                            empresa=empresa,
                            ativo=True
                        ).order_by("nome")
                    )
        else:
            raise Exception(f"Erro no form {self.__class__.__name__}, empresa não está na sessão.")
