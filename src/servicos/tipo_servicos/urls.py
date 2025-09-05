from django.urls import path

from servicos.tipo_servicos.views import TipoServicoListView, TipoServicoCreateView


app_name = "tipo_servicos"

urlpatterns = [
    path('', TipoServicoListView.as_view(), name="list"),
    path('novo/', TipoServicoCreateView.as_view(), name="create")
]
