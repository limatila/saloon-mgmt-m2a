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


class DateHierarchyAdmin(BaseAdmin):
    date_hierarchy = "data_criado"