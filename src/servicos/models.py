from cadastros.empresas.models import BaseAssociadoEmpresa


class BaseServicosModel(BaseAssociadoEmpresa):
    module_label = "servicos"

    class Meta:
        abstract = True