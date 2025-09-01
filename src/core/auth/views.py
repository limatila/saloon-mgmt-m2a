from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.forms import Form, ValidationError
from django.contrib.auth import authenticate, login, get_user_model, logout

from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse_lazy

from core.auth.forms import UserForm, LogoutForm

GLOBAL_AUTH_TEMPLATE = "auth/auth.html"

#* Entrada
class LoginView(FormView):
    template_name = GLOBAL_AUTH_TEMPLATE
    form_class = UserForm
    success_url = reverse_lazy('home')
    redirect_field_name = "next"

    def form_valid(self, form: Form):
        usuario = form.cleaned_data['username']
        senha = form.cleaned_data['password']

        user = authenticate(self.request, username=usuario, password=senha)

        if user:
            if self.request.user.is_authenticated:
                logout(self.request)

            login(self.request, user)
            url_redirecionamento = self.request.GET.get(self.redirect_field_name) or self.request.POST.get(self.redirect_field_name)

            # Validate redirection
            if url_redirecionamento and url_has_allowed_host_and_scheme(url_redirecionamento, allowed_hosts=(self.request.get_host())):
                return redirect(url_redirecionamento)

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
    template_name = GLOBAL_AUTH_TEMPLATE
    success_url = reverse_lazy('home')

    def form_valid(self, form: Form):
        usuario: str = form.cleaned_data['username']
        senha: str = form.cleaned_data['password']
        
        try:
            User = get_user_model()
            user = User.objects.create_user(username=usuario, password=senha, email='none@mail.com')
            user.first_name = usuario.split()[0]
            user.last_name = "".join(usuario.split()[1:])
            user.save()
        except Exception as err:
            raise err

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Registrar sua conta"
        contexto["form_name"] = "Registro"
        return contexto


#* Saída
class LogoutView(FormView, TemplateView):
    template_name = GLOBAL_AUTH_TEMPLATE
    form_class = LogoutForm
    success_url = reverse_lazy('home')
    http_method_names = ['get', 'post']

    def form_valid(self, form: Form):
        senha = form.cleaned_data['password']
        user = self.request.user

        if not user.is_authenticated:
            return redirect(reverse_lazy('core:auth:login'))

        if not user.check_password(senha):
            form.add_error(None, ValidationError("Senha incorreta para deslogar usuário da sessão. Fale com administrador."))
            return self.form_invalid(form)

        logout(self.request)
        return redirect(self.get_next_page())

    def get_next_page(self):
        url_redirecionamento = self.request.META.get('HTTP_REFERER')

        condicao_url_valida: bool = url_redirecionamento and url_has_allowed_host_and_scheme(url_redirecionamento, allowed_hosts={self.request.get_host()})
        condicao_redirecionamento_valido = (not "logout" in url_redirecionamento)
        if condicao_url_valida and condicao_redirecionamento_valido:
            return url_redirecionamento

        return self.success_url

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Sair da conta"
        contexto["form_name"] = "Logout"
        return contexto
