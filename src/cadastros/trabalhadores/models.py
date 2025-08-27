from django.db import models
from core.pessoas.models import Pessoa


class Trabalhador(Pessoa):
    class Meta:
        verbose_name_plural = "Trabalhadores"