from django.urls import path, include


app_name = "cadastros"

urlpatterns = [
    path("clientes/", include('cadastros.clientes.urls', namespace='clientes')),
    # path("empresas/", include('cadastros.empresas.urls', namespace='empresas')),
    # path("tipo_servicos/", include('cadastros.tipo_servicos.urls', namespace='tipo_servicos')),
    # path("trabalhadores/", include('cadastros.trabalhadores.urls', namespace='trabalhadores'))
]