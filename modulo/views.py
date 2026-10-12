from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ComponenteForm, FiltroComponenteForm
from .models import Componente

POR_PAGINA = 5


def _mis_componentes(request):
    # Cada usuario solo ve y gestiona sus propios componentes.
    return Componente.objects.filter(usuario=request.user)


@login_required
def componente_lista(request):
    componentes = _mis_componentes(request)
    filtro = FiltroComponenteForm(request.GET or None)

    if filtro.is_valid():
        datos = filtro.cleaned_data
        if datos['q']:
            componentes = componentes.filter(
                Q(nombre__icontains=datos['q']) | Q(descripcion__icontains=datos['q'])
            )
        if datos['categoria']:
            componentes = componentes.filter(categoria=datos['categoria'])
        if datos['en_uso'] in ('0', '1'):
            componentes = componentes.filter(en_uso=datos['en_uso'] == '1')
        if datos['orden']:
            componentes = componentes.order_by(datos['orden'], 'nombre')

    paginator = Paginator(componentes, POR_PAGINA)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Querystring de los filtros SIN el parámetro 'page', para que los enlaces
    # de paginación conserven los filtros aplicados.
    parametros = request.GET.copy()
    parametros.pop('page', None)

    return render(request, 'modulo/componente_lista.html', {
        'page_obj': page_obj,
        'filtro': filtro,
        'querystring': parametros.urlencode(),
        'total': paginator.count,
    })


@login_required
def componente_detalle(request, pk):
    componente = get_object_or_404(_mis_componentes(request), pk=pk)
    return render(request, 'modulo/componente_detalle.html', {'componente': componente})


@login_required
def componente_crear(request):
    form = ComponenteForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        componente = form.save()
        messages.success(request, f'Componente "{componente.nombre}" creado.')
        return redirect(componente)
    return render(request, 'modulo/componente_form.html', {'form': form, 'titulo': 'Nuevo componente'})


@login_required
def componente_editar(request, pk):
    componente = get_object_or_404(_mis_componentes(request), pk=pk)
    form = ComponenteForm(request.POST or None, instance=componente, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Componente "{componente.nombre}" actualizado.')
        return redirect(componente)
    return render(request, 'modulo/componente_form.html',
                  {'form': form, 'titulo': f'Editar: {componente.nombre}', 'componente': componente})


@login_required
def componente_eliminar(request, pk):
    componente = get_object_or_404(_mis_componentes(request), pk=pk)
    if request.method == 'POST':
        nombre = componente.nombre
        componente.delete()
        messages.success(request, f'Componente "{nombre}" eliminado.')
        return redirect('componente_lista')
    return render(request, 'modulo/componente_confirmar_eliminar.html', {'componente': componente})
