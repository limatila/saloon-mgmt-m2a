from django import forms

from validate_docbr import CPF


class BasePessoasForm(forms.ModelForm):
    class Meta:
        fields = ['nome', 'cpf', 'imagem', 'telefone', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-field', 'placeholder': "nome de nome"}),
            'cpf': forms.TextInput(attrs={'class': 'form-field', 'placeholder': "XXX.XXX.XXX-xx"}),
            'telefone': forms.TextInput(attrs={'class': 'form-field', 'placeholder': "+55 (XX) xxxx.xxxx"}),
            'endereco': forms.TextInput(attrs={'class': 'form-field', 'placeholder': "nome de nome"}),
            'imagem': forms.FileInput(attrs={'class': 'form-field'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            validator = CPF()
            charsToRemove = [' ', '.', '-']
            for char in charsToRemove:
                cpf = cpf.replace(char, '')   
            if not validator.validate(cpf):
                raise forms.ValidationError("CPF não é válido")
        return cpf
    
    def clean_telefone(self):
        number: str = self.cleaned_data.get('telefone')
        if number:
            charsToRemove = [' ', '(', ')']
            if not number.startswith('+'):
                raise forms.ValidationError('Número de telefone deve começar com \'+\'')
            for char in charsToRemove:
                number = number.replace(char, '')
        return number
