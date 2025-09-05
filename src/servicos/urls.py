from django.urls import path, include

from servicos.views import ServicosSubmodulesView


app_name = "servicos"

urlpatterns = [
    path("", ServicosSubmodulesView.as_view(), name="list"), 
    path("agendamentos/", include('servicos.agendamentos.urls', namespace="agendamentos")),
    path("servicos/", include('servicos.tipo_servicos.urls', namespace="tipo_servicos"))
]
