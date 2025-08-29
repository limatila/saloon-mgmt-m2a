from django.urls import path, include

from cadastros.tipo_servicos.views import TipoServicoListView


app_name = "tipo_servicos"

urlpatterns = [
    path('', TipoServicoListView.as_view(), name="list")
]
