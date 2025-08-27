from django.db import models

from core.bases.models import BaseModel


class Pessoa(BaseModel):
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

    def __str__(self):
        return f"{self.id} - {self.nome}"

    class Meta:
        abstract = True