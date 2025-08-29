from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    list_display = ['data_criado', 'data_modificado']
    list_per_page = 20
    list_max_show_all = 100
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
    
    def get_list_display(self, request):
        base_list = list(super().get_list_display(request))

        new_list = ["empresa", ]

        return new_list + base_list

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