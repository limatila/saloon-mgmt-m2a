from django.db import models

from core.bases.models import BaseAssociadoEmpresa


class Pessoa(BaseAssociadoEmpresa):
    nome = models.CharField(
        verbose_name="Nome",
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
    imagem = models.ImageField(
        verbose_name="Imagem",
        default="placeholder.jpg",
        upload_to="imagens-pessoas/",
        null=True,
        blank=True,
        editable=True
    )
    telefone = models.CharField(
        verbose_name="Telefone",
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