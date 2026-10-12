from django import forms

from .models import Componente


class ComponenteForm(forms.ModelForm):
    class Meta:
        model = Componente
        # 'usuario' no se pide: se asigna automáticamente con el usuario logueado.
        fields = ['nombre', 'categoria', 'descripcion', 'cantidad',
                  'precio_unitario', 'fecha_compra', 'en_uso']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'fecha_compra': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'en_uso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        if usuario is not None:
            self.instance.usuario = usuario

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        qs = Componente.objects.filter(usuario_id=self.instance.usuario_id,
                                       nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya tienes un componente registrado con ese nombre.')
        return nombre


class FiltroComponenteForm(forms.Form):
    """Filtros de la vista de lista (se envían por GET para convivir con la paginación)."""
    q = forms.CharField(
        label='Buscar', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre o descripción'}),
    )
    categoria = forms.ChoiceField(
        label='Categoría', required=False,
        choices=[('', 'Todas')] + list(Componente.Categoria.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    en_uso = forms.ChoiceField(
        label='Estado', required=False,
        choices=[('', 'Todos'), ('1', 'En uso'), ('0', 'Disponible')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    orden = forms.ChoiceField(
        label='Ordenar por', required=False,
        choices=[('', 'Más recientes'), ('nombre', 'Nombre A-Z'),
                 ('-cantidad', 'Mayor cantidad'), ('precio_unitario', 'Menor precio'),
                 ('-precio_unitario', 'Mayor precio')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
