from django.contrib import admin

from core.admin import PersonAdmin
from cadastros.clientes.models import Cliente

@admin.register(Cliente)
class ClienteAdmin(PersonAdmin):
    pass
