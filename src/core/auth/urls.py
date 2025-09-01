from django.urls import path

from core.auth.views import LoginView, SignUpView, LogoutView


app_name = "auth"

urlpatterns = [
    path("sign/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout")
]
