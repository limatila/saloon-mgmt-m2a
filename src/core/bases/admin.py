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


class DateHierarchyAdmin(BaseAdmin):
    date_hierarchy = "data_criado"
