from django.urls import path
from . import views

urlpatterns = [
    path('', views.componente_lista, name='componente_lista'),
    path('componentes/nuevo/', views.componente_crear, name='componente_crear'),
    path('componentes/<int:pk>/', views.componente_detalle, name='componente_detalle'),
    path('componentes/<int:pk>/editar/', views.componente_editar, name='componente_editar'),
    path('componentes/<int:pk>/eliminar/', views.componente_eliminar, name='componente_eliminar'),
]
