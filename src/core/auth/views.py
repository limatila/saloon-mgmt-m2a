from django.forms import ValidationError
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy

from core.auth.forms import UserForm, forms


class LoginView(FormView):
    template_name = "auth/login.html"
    form_class = UserForm
    success_url = reverse_lazy('home')

    def form_valid(self, form: forms.Form):
        usuario = form.cleaned_data['username']
        senha = form.cleaned_data['password']

        user = authenticate(self.request, username=usuario, password=senha)

        if user:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, ValidationError("Usuário e/ou Senha são inválidos."))
            return self.form_invalid(form)
        
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Logar na Conta"
        contexto["form_name"] = "Login"
        contexto["sidebar"] = False
        return contexto


class SignUpView(LoginView):
    def form_valid(self, form: forms.Form):
        form.save() #salva depois loga
        return super().form_valid(form)
        
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Registrar sua conta"
        contexto["form_name"] = "Sign Up"
        return contexto
    