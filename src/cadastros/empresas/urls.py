from django.urls import path, include

from cadastros.empresas.views import SelecaoEmpresasListView


app_name = "empresas"

urlpatterns = [
    path('select/', SelecaoEmpresasListView.as_view(), name="select")
]
