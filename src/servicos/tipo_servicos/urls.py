from django.urls import path

from servicos.tipo_servicos.views import TipoServicoListView, TipoServicoCreateView, TipoServicoDeleteView


app_name = "tipo_servicos"

urlpatterns = [
    path('', TipoServicoListView.as_view(), name="list"),
    path('novo/', TipoServicoCreateView.as_view(), name="create"),
    path("deletar/<int:pk>/", TipoServicoDeleteView.as_view(), name="delete")
]
