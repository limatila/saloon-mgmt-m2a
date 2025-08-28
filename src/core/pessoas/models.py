from django.db import models

from core.bases.models import BaseAssociadoEmpresa


class Pessoa(BaseAssociadoEmpresa):
    nome = models.CharField(
        null=False,
        blank=False,
        max_length=255
    )
    cpf = models.CharField(
        verbose_name="CPF",
        null=False,
        blank=False,
        max_length=11,
        unique=True
    )
    ativo = models.BooleanField(
        default=True,
        null=False,
        blank=False
    )
    image = models.ImageField(
        default="placeholder.jpg",
        upload_to="imagens-pessoas/",
        null=True,
        blank=True,
        editable=True
    )
    telefone = models.CharField(
        max_length=21,
        null=False,
        blank=False,
        unique=True
    )
    endereco = models.CharField(
        verbose_name="Endereço",
        null=False,
        blank=False
    )

    class Meta:
        abstract = True