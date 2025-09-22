from django import forms
from django.contrib.auth import get_user_model


class UserForm(forms.Form):
    usuario = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-field', 'placeholder': "Nome, Username..."})
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-field', 'placeholder': "***.."})
    )

class LogoutForm(forms.Form):
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-field', 'placeholder': "***.."})
    )
