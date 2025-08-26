from django.contrib import admin

class PersonAdmin(admin.ModelAdmin):
    search_fields = "nome", "cpf", "telefone", "endereco"
    search_help_text = "Nome, cpf, telefone ou endereço..."

class DateHierarchyAdmin(admin.ModelAdmin):
    date_hierarchy = "data_criado"