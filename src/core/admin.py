from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ['data_criado', 'data_modificado']
    fieldsets = [
        (
            'Core',
            {
                'fields': ('data_criado', 'data_modificado')
            }
        )
    ]


class PersonAdmin(BaseAdmin):
    search_fields = "nome", "cpf", "telefone", "endereco"
    search_help_text = "Nome, cpf, telefone ou endereço..."
    
    def get_fieldsets(self, request, obj = ...):
        base_fieldsets = list(super().get_fieldsets(request, obj))
        
        new_fieldsets = [
            (
                "Basic",
                {
                    'fields': ('nome', 'cpf')
                }
            ),
            (
                "Additional",
                {
                    'classes': ('collapse', ),
                    'fields': ('telefone', )
                }
            )
        ]
        
        return base_fieldsets + new_fieldsets


class DateHierarchyAdmin(admin.ModelAdmin):
    date_hierarchy = "data_criado"