from django.contrib import admin

from .models import Componente


@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'cantidad', 'precio_unitario',
                    'fecha_compra', 'en_uso', 'usuario')
    list_filter = ('categoria', 'en_uso', 'usuario')
    search_fields = ('nombre', 'descripcion')
