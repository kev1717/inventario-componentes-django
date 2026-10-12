from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Componente(models.Model):
    """Componente electrónico del inventario personal de un usuario."""

    class Categoria(models.TextChoices):
        RESISTENCIA = 'RES', 'Resistencia'
        CAPACITOR = 'CAP', 'Capacitor'
        SEMICONDUCTOR = 'SEM', 'Semiconductor (diodo, transistor)'
        CIRCUITO_INTEGRADO = 'CI', 'Circuito integrado'
        MICROCONTROLADOR = 'MCU', 'Microcontrolador / placa'
        SENSOR = 'SEN', 'Sensor'
        OTRO = 'OTR', 'Otro'

    # Relación con el modelo Usuario: cada componente pertenece a un usuario.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='componentes',
        verbose_name='usuario',
    )
    nombre = models.CharField('nombre', max_length=100)
    categoria = models.CharField(
        'categoría', max_length=3, choices=Categoria.choices, default=Categoria.OTRO
    )
    descripcion = models.TextField('descripción', blank=True)
    cantidad = models.PositiveIntegerField(
        'cantidad', default=1, validators=[MaxValueValidator(10000)]
    )
    precio_unitario = models.DecimalField(
        'precio unitario (COP)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    fecha_compra = models.DateField('fecha de compra', default=timezone.localdate)
    en_uso = models.BooleanField('¿en uso en un proyecto?', default=False)
    creado = models.DateTimeField('creado', auto_now_add=True)

    class Meta:
        verbose_name = 'componente'
        verbose_name_plural = 'componentes'
        ordering = ['-fecha_compra', 'nombre']
        constraints = [
            # Un usuario no puede registrar dos veces el mismo componente.
            models.UniqueConstraint(
                fields=['usuario', 'nombre'], name='componente_unico_por_usuario'
            ),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.get_categoria_display()})'

    def clean(self):
        # Regla de validación propia: la fecha de compra no puede ser futura.
        if self.fecha_compra and self.fecha_compra > timezone.localdate():
            raise ValidationError(
                {'fecha_compra': 'La fecha de compra no puede estar en el futuro.'}
            )
        # Regla de negocio: no puede estar "en uso" si no hay unidades.
        if self.en_uso and self.cantidad == 0:
            raise ValidationError(
                {'en_uso': 'No puede estar en uso un componente con cantidad 0.'}
            )

    @property
    def valor_total(self):
        return self.cantidad * self.precio_unitario

    def get_absolute_url(self):
        return reverse('componente_detalle', args=[self.pk])
