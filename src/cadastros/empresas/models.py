from django.db import models
from django.conf import settings

from core.bases.models import BaseModel


class Empresa(BaseModel):
    cnpj = models.CharField(
        verbose_name="CNPJ",
        max_length=14,
        unique=True,
        null=False,
        blank=False,
        default=None
    )
    nome_fantasia = models.CharField(
        verbose_name="Nome-fantasia",
        max_length=255,
        null=False,
        blank=False,
        default=None
    )
    razao_social = models.CharField(
        verbose_name="Razão Social",
        max_length=255,
        null=False,
        blank=False,
        default=None
    )
    imagem = models.ImageField(
        verbose_name="Imagem da empresa",
        default="placeholder-empresa.jpg",
        upload_to="imagens-empresas/",
        null=True,
        blank=True,
        editable=True
    )

    #FKs
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name="Usuário",
        null=False,
        blank=False,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.id} - {self.nome_fantasia}"

class BaseAssociadoEmpresa(BaseModel):
    empresa = models.ForeignKey(
        'empresas.Empresa',
        verbose_name="Empresa",
        null=False,
        blank=False,
        on_delete=models.PROTECT
    )

    class Meta:
        abstract = True
