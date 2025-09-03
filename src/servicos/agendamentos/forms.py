from django import forms
from servicos.agendamentos.models import Agendamento


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