from django.contrib import admin

from core.admin import PersonAdmin
from cadastros.trabalhadores.models import Trabalhador


@admin.register(Trabalhador)
class TrabalhadorAdmin(PersonAdmin):
    pass