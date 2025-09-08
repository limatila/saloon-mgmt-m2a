from django.db import models

from cadastros.models import BaseCadastrosModel


class Pessoa(BaseCadastrosModel):
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
        verbose_name="Foto da Pessoa",
        default="placeholder-pessoa.jpg",
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