from django.db import models


class BaseModel(models.Model):
    data_criado = models.DateTimeField(
        verbose_name="Data de Criação",
        auto_now_add=True,
        null=False,
        blank=False
    )
    data_modificado = models.DateTimeField(
        verbose_name="Data de Modificação",
        auto_now=True,
        null=False,
        blank=False
    )

    class Meta:
        abstract = True


class BaseAssociadoEmpresa(BaseModel):
    empresa = models.ForeignKey(
        'empresas.Empresa',
        null=False,
        blank=False,
        on_delete=models.PROTECT
    )

    class Meta:
        abstract = True