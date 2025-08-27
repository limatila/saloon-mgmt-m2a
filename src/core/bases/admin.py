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

class BaseAssociadoEmpresaAdmin(BaseAdmin):
    raw_id_fields = "empresa", 
    
    def get_fieldsets(self, request, obj = ...):
        base_fieldsets = list(super().get_fieldsets(request, obj))

        new_fieldsets = [
            (
                "Empresas",
                {
                    'fields': ('empresa', )
                }
            ),
        ]
        
        return base_fieldsets + new_fieldsets


class DateHierarchyAdmin(BaseAdmin):
    date_hierarchy = "data_criado"