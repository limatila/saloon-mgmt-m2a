from django.db import models
from core.pessoas.models import Pessoa



class Trabalhador(Pessoa):
    telefone = models.CharField(
        max_length=21,
        null=True,
        unique=True
    )
    class Meta:
        verbose_name_plural = "Trabalhadores"