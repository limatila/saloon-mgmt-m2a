from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.forms import Form, ValidationError
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib import messages

from django.shortcuts import redirect
from django.urls import reverse_lazy

from core.auth.forms import UserForm, LogoutForm


GLOBAL_AUTH_TEMPLATE = "partials/components/dashboards/form-dashboard.html"


#* Entrada
class LoginView(FormView):
    template_name = GLOBAL_AUTH_TEMPLATE
    form_class = UserForm
    success_url = reverse_lazy('cadastros:empresas:select')
    redirect_field_name = "next"

    def form_valid(self, form: Form):
        usuario = form.cleaned_data['username']
        senha = form.cleaned_data['password']

        user = authenticate(self.request, username=usuario, password=senha)

        if user:
            if self.request.user.is_authenticated:
                logout(self.request)
            login(self.request, user)

            #redirect to sucess_url
            metodo_GET = self.request.GET
            metodo_POST = self.request.POST
            url_redirecionamento = (
                metodo_GET.get(self.redirect_field_name) or metodo_POST.get(self.redirect_field_name)
            )

            # Validate redirection
            if url_redirecionamento:
                return redirect(url_redirecionamento)

            messages.success(self.request, "✅ Login realizado com sucesso!")
            return super().form_valid(form)
        else:
            messages.warning(self.request, "⛔ Login falhou!")
            form.add_error(None, ValidationError("Usuário e/ou Senha são inválidos."))
            return self.form_invalid(form)
        
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Logar na Conta"
        contexto["description"] = "Entre na sua conta autorizada."
        contexto["form_name"] = "Login"
        contexto["sidebar"] = False
        return contexto


class SignUpView(LoginView):
    template_name = GLOBAL_AUTH_TEMPLATE
    success_url = reverse_lazy('home')

    def form_valid(self, form: Form):   #TODO não ativar, disponibilizar para a staff verificar
        usuario: str = form.cleaned_data['username']
        senha: str = form.cleaned_data['password']

        try:
            User = get_user_model()
            user = User.objects.create_user(username=usuario, password=senha, email='none@mail.com')
            user.first_name = usuario.split()[0]
            user.last_name = " ".join(usuario.split()[1:])
            user.save()
            messages.success(self.request, "✅ Cadastro realizado com sucesso!")
        except Exception as err:
            raise err

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Registrar sua conta"
        contexto["description"] = "Crie uma nova conta para o nosso SaaS. A confirmação acontece em segundos!"
        contexto["form_name"] = "Registro"
        return contexto


#* Saída
class LogoutView(FormView, TemplateView):
    template_name = GLOBAL_AUTH_TEMPLATE
    form_class = LogoutForm
    success_url = reverse_lazy('home')
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "⛔ Logue em uma conta!")
            return redirect(reverse_lazy('core:auth:login'))
        
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: Form):
        senha = form.cleaned_data['password']
        user = self.request.user

        if not user.check_password(senha):
            form.add_error(None, ValidationError("Senha incorreta para deslogar usuário da sessão. Fale com administrador."))
            return self.form_invalid(form)

        logout(self.request)
        messages.success(self.request, "✅ Logout realizado com sucesso, você saiu da sua conta!")
        return redirect(self.get_next_page())

    def get_next_page(self):
        url_redirecionamento = self.request.META.get('HTTP_REFERER')

        if not "logout" in url_redirecionamento:
            return url_redirecionamento

        return self.success_url

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Sair da conta"
        contexto["description"] = "Saia com sua senha. Depois poderá logar com outra conta."
        contexto["form_name"] = "Logout"
        return contexto
