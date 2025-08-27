from django.db import models
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
