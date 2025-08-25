from django.contrib import admin
from saloon.models import *

# Register your models here.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    pass
@admin.register(Trabalhador)
class TrabalhadorAdmin(admin.ModelAdmin):
    list_filter = ""
@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    pass
@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    pass