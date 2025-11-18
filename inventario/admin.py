from django.contrib import admin
from django.http import HttpResponse
from simple_history.admin import SimpleHistoryAdmin
from .models import Libro, TrabajoGrado
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
import qrcode
from io import BytesIO


def imprimir_etiquetas_qr(modeladmin, request, queryset):
    """Genera un PDF con etiquetas QR para los registros seleccionados"""
    # Crear el objeto HttpResponse con el header PDF apropiado
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etiquetas_qr.pdf"'
    
    # Crear el PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    # Configuración de etiquetas
    etiqueta_width = 5 * cm
    etiqueta_height = 3 * cm
    margen = 1 * cm
    
    # Posición inicial
    x = margen
    y = height - margen - etiqueta_height
    
    for idx, item in enumerate(queryset):
        # Generar código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(item.codigo_nuevo)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir imagen QR a bytes
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Dibujar etiqueta
        # Marco
        p.rect(x, y, etiqueta_width, etiqueta_height)
        
        # Código
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x + 0.2*cm, y + etiqueta_height - 0.5*cm, item.codigo_nuevo)
        
        # Título (truncado)
        titulo_truncado = item.titulo[:35] + "..." if len(item.titulo) > 35 else item.titulo
        p.setFont("Helvetica", 8)
        p.drawString(x + 0.2*cm, y + etiqueta_height - 1*cm, titulo_truncado)
        
        # Código QR
        p.drawInlineImage(buffer, x + 0.2*cm, y + 0.2*cm, width=2*cm, height=2*cm)
        
        # Mover a la siguiente posición
        x += etiqueta_width + 0.5*cm
        
        # Si llegamos al final de la línea, bajar
        if x + etiqueta_width > width - margen:
            x = margen
            y -= etiqueta_height + 0.5*cm
        
        # Si llegamos al final de la página, crear nueva página
        if y < margen:
            p.showPage()
            x = margen
            y = height - margen - etiqueta_height
    
    p.showPage()
    p.save()
    return response

imprimir_etiquetas_qr.short_description = "Imprimir etiquetas QR"


@admin.register(Libro)
class LibroAdmin(SimpleHistoryAdmin):
    list_display = ('codigo_nuevo', 'titulo', 'autor', 'materia', 'ubicacion_seccion', 'estado', 'anio')
    list_filter = ('estado', 'anio', 'materia', 'ubicacion_seccion')
    search_fields = ('codigo_nuevo', 'titulo', 'autor', 'materia', 'editorial')
    readonly_fields = ('fecha_registro',)
    actions = [imprimir_etiquetas_qr]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo_nuevo', 'codigo_antiguo', 'titulo', 'autor')
        }),
        ('Detalles del Libro', {
            'fields': ('materia', 'editorial', 'edicion', 'anio')
        }),
        ('Ubicación', {
            'fields': ('codigo_seccion_full', 'ubicacion_seccion', 'ubicacion_repisa')
        }),
        ('Estado', {
            'fields': ('estado', 'observaciones', 'fecha_registro')
        }),
    )
    
    list_per_page = 50


@admin.register(TrabajoGrado)
class TrabajoGradoAdmin(SimpleHistoryAdmin):
    list_display = ('codigo_nuevo', 'titulo', 'autor', 'tutor', 'modalidad', 'carrera', 'anio')
    list_filter = ('modalidad', 'carrera', 'facultad', 'anio', 'estado')
    search_fields = ('codigo_nuevo', 'titulo', 'autor', 'tutor', 'carrera')
    readonly_fields = ('fecha_registro',)
    actions = [imprimir_etiquetas_qr]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo_nuevo', 'codigo_antiguo', 'titulo')
        }),
        ('Información Académica', {
            'fields': ('autor', 'tutor', 'modalidad', 'carrera', 'facultad', 'anio')
        }),
        ('Ubicación', {
            'fields': ('ubicacion_seccion', 'ubicacion_repisa')
        }),
        ('Estado', {
            'fields': ('estado', 'observaciones', 'fecha_registro')
        }),
    )
    
    list_per_page = 50
