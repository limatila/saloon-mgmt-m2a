from django.urls import path, include


app_name = "servicos"

urlpatterns = [
    path("agendamentos/", include('servicos.agendamentos.urls', namespace="agendamentos"))
]
