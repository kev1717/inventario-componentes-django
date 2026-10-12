# Inventario de Componentes Electrónicos — Django MPA

Trabajo en Clase 2 · Programación en la Web (G2) · UIS
Estudiante: Kevin David Basto Quintero — 2222974

Aplicación MPA en Django que permite a cada usuario llevar el inventario de sus
componentes electrónicos (resistencias, capacitores, sensores, microcontroladores…),
con CRUD completo, paginación y filtros.

## Cómo ejecutarlo

```bash
pip install django
python manage.py migrate
python manage.py runserver
```

1. Entra a http://127.0.0.1:8000/admin/ con **admin / admin** (esto crea la sesión).
2. Ve a http://127.0.0.1:8000/ — ahí está la lista de componentes.

La base de datos ya incluye 12 componentes de ejemplo del usuario `admin`.

## Fase 1 — Modelo `Componente` (modulo/models.py)

| Campo | Tipo | Justificación |
|---|---|---|
| `usuario` | `ForeignKey(User)` | Relación pedida con el modelo Usuario. Cada componente pertenece a un usuario; `on_delete=CASCADE` porque si se borra el usuario su inventario deja de tener sentido. |
| `nombre` | `CharField(100)` | Campo de texto principal para identificar el componente. |
| `categoria` | `CharField` con `choices` | Lista cerrada (Resistencia, Capacitor, Sensor…) para evitar escribir la misma categoría de formas distintas y poder filtrar por ella. |
| `descripcion` | `TextField` (opcional) | Texto libre para notas: valor, encapsulado, proyecto donde se usa. |
| `cantidad` | `PositiveIntegerField` | Numérico: no tiene sentido una cantidad negativa. Máximo 10 000. |
| `precio_unitario` | `DecimalField(10,2)` | Decimal (no float) para manejar dinero sin errores de redondeo; mínimo 0. |
| `fecha_compra` | `DateField` | Tipo fecha; por defecto el día de hoy. |
| `en_uso` | `BooleanField` | Indica si el componente está montado en un proyecto. |
| `creado` | `DateTimeField(auto_now_add)` | Auditoría: cuándo se registró. |

### Restricciones y reglas de validación propias
1. **Nombre único por usuario** (`UniqueConstraint(usuario, nombre)` + validación en el formulario sin distinguir mayúsculas): evita registrar dos veces el mismo componente.
2. **La fecha de compra no puede ser futura** (`clean()` del modelo).
3. **No puede estar "en uso" si la cantidad es 0** (`clean()` del modelo).
4. `cantidad` ≥ 0 y ≤ 10 000; `precio_unitario` ≥ 0 (validadores).

Además se agregó la propiedad calculada `valor_total = cantidad × precio_unitario`, que se muestra en el detalle.

### Migración y verificación
```bash
python manage.py makemigrations modulo
python manage.py migrate
```
Con **DB Browser for SQLite** se abre una copia de `db.sqlite3` y se verifica la tabla `modulo_componente`.
El modelo está registrado en el admin (`modulo/admin.py`) con columnas, filtros y búsqueda.

## Fase 2 — CRUD

| Operación | URL | Vista | Template |
|---|---|---|---|
| Listar | `/` | `componente_lista` | `componente_lista.html` |
| Crear | `/componentes/nuevo/` | `componente_crear` | `componente_form.html` |
| Detalle | `/componentes/<id>/` | `componente_detalle` | `componente_detalle.html` |
| Editar | `/componentes/<id>/editar/` | `componente_editar` | `componente_form.html` |
| Eliminar | `/componentes/<id>/eliminar/` | `componente_eliminar` | `componente_confirmar_eliminar.html` |

- Formulario `ComponenteForm` en `forms.py` (ModelForm). El campo `usuario` **no se pide**: se asigna automáticamente con el usuario que tiene la sesión iniciada.
- Todas las vistas usan `@login_required` (redirige a `/admin/login/`) y cada usuario solo ve/edita/elimina **sus propios** componentes (si intenta abrir uno ajeno, obtiene 404).
- La eliminación pide confirmación y se hace por POST.
- Estilos con **Bootstrap 5** (CDN) y mensajes de éxito con `django.contrib.messages`.

## Fase 3 — Paginación y filtrado

- Paginación con el `Paginator` incluido en Django (5 registros por página), sin paquetes extra.
- Filtros en `FiltroComponenteForm` (enviados por **GET**):
  - Búsqueda por texto en nombre o descripción.
  - Categoría.
  - Estado (en uso / disponible).
  - Ordenamiento (recientes, nombre, cantidad, precio).
- **Compatibilidad filtros + paginación:** la vista reconstruye el querystring de los filtros sin el parámetro `page`, y cada enlace de página lo incluye (`?categoria=SEN&q=...&page=2`), así los filtros no se pierden al cambiar de página.
