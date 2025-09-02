from django.urls import path, include

from core.bases.views import HomePageView


app_name = "servicos"

urlpatterns = [
    path("", HomePageView.as_view(), name="list"), #! TROCAR APÓS IMPLEMENTAÇÃO
    path("agendamentos/", include('servicos.agendamentos.urls', namespace="agendamentos"))
]
