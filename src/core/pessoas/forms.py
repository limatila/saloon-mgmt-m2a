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
            'imagem': forms.FileInput(attrs={'class': 'form-field', 'required': 'False'}),
        }

    def clean_phone_number(self):
        number: str = self.cleaned_data.get('phone_number')
        if number:
            charsToRemove = [' ', '(', ')']
            if not number.startswith('+'):
                raise forms.ValidationError('Phone number must start with \'+\'')
            for char in charsToRemove:
                number = number.replace(char, '')
        return number
    
    def clean_CPF(self):
        cpf = self.cleaned_data.get('CPF')
        if cpf:
            validator = CPF()
            charsToRemove = [' ', '.', '-']
            for char in charsToRemove:
                cpf = cpf.replace(char, '')   
            if not validator.validate(cpf):
                raise forms.ValidationError("CPF is not valid.")
        return cpf