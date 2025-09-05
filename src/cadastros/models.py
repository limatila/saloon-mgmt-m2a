from django.db import models

from cadastros.empresas.models import BaseAssociadoEmpresa

class BaseCadastrosModel(BaseAssociadoEmpresa):
    module_label = "cadastros"
    
    class Meta:
        abstract = True