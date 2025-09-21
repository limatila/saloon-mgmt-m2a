from django import forms
from django.contrib.auth import get_user_model


class UserForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-field', 'placeholder': "Nome, Username..."})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-field', 'placeholder': "***.."})
    )

class LogoutForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-field', 'placeholder': "***.."})
    )
