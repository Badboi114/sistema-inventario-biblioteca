from django.db import models
from simple_history.models import HistoricalRecords
from datetime import timedelta
from django.utils import timezone


class ActivoBibliografico(models.Model):
    """Clase base para todos los activos bibliográficos de la biblioteca"""
    
    ESTADO_CHOICES = [
        ('BUENO', 'Bueno'),
        ('REGULAR', 'Regular'),
        ('MALO', 'Malo'),
        ('EN REPARACION', 'En Reparación'),
    ]
    
    # Permite múltiples registros sin código (NULL). Los códigos existentes siguen siendo únicos.
    codigo_nuevo = models.CharField(max_length=50, null=True, blank=True, db_index=True, verbose_name='Código Nuevo')
    codigo_antiguo = models.CharField(max_length=50, null=True, blank=True, verbose_name='Código Antiguo')
    titulo = models.CharField(max_length=500, verbose_name='Título')
    autor = models.CharField(max_length=300, blank=True, null=True, verbose_name='Autor')
    anio = models.IntegerField(null=True, blank=True, verbose_name='Año')
    facultad = models.CharField(max_length=255, blank=True, null=True, verbose_name='Facultad')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BUENO', blank=True, verbose_name='Estado')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    ubicacion_seccion = models.CharField(max_length=50, blank=True, null=True, verbose_name='Ubicación - Sección')
    ubicacion_repisa = models.CharField(max_length=50, blank=True, null=True, verbose_name='Ubicación - Repisa')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    
    # Historial de cambios para auditoría
    history = HistoricalRecords(inherit=True)
    
    # Propiedad para identificar el tipo de activo
    @property
    def tipo_activo(self):
        """Devuelve el tipo de activo: LIBRO o TESIS"""
        if hasattr(self, 'libro'):
            return 'LIBRO'
        if hasattr(self, 'trabajogrado'):
            return 'TESIS'
        return 'OTRO'
    
    class Meta:
        verbose_name = 'Activo Bibliográfico'
        verbose_name_plural = 'Activos Bibliográficos'
        ordering = ['codigo_nuevo']
    
    def __str__(self):
        return self.titulo


class Libro(ActivoBibliografico):
    """Modelo para libros de la biblioteca"""
    
    materia = models.CharField(max_length=200, blank=True, null=True, verbose_name='Materia')
    editorial = models.CharField(max_length=200, blank=True, null=True, verbose_name='Editorial')
    edicion = models.CharField(max_length=100, blank=True, null=True, verbose_name='Edición')
    codigo_seccion_full = models.CharField(max_length=100, blank=True, null=True, verbose_name='Código Completo de Sección')
    orden_importacion = models.IntegerField(default=0, verbose_name='Orden de Importación', db_index=True)
    
    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
        ordering = ['orden_importacion']
    
    def __str__(self):
        return self.titulo


class TrabajoGrado(ActivoBibliografico):
    """Modelo para trabajos de grado (tesis, proyectos, trabajos dirigidos)"""
    
    MODALIDAD_CHOICES = [
        ('TESIS', 'Tesis'),
        ('PROYECTO DE GRADO', 'Proyecto de Grado'),
        ('TRABAJO DIRIGIDO', 'Trabajo Dirigido'),
    ]
    
    modalidad = models.CharField(max_length=30, choices=MODALIDAD_CHOICES, blank=True, null=True, verbose_name='Modalidad')
    tutor = models.CharField(max_length=300, blank=True, null=True, verbose_name='Tutor')
    carrera = models.CharField(max_length=200, blank=True, null=True, verbose_name='Carrera')
    
    class Meta:
        verbose_name = 'Trabajo de Grado'
        verbose_name_plural = 'Trabajos de Grado'
    
    def __str__(self):
        return self.titulo


class Estudiante(models.Model):
    """Modelo para estudiantes que solicitan préstamos"""
    
    nombre_completo = models.CharField(max_length=255, verbose_name='Nombre Completo')
    carnet_universitario = models.CharField(max_length=50, unique=True, verbose_name='Carnet Universitario')
    ci = models.CharField(max_length=20, unique=True, verbose_name='Cédula de Identidad')
    carrera = models.CharField(max_length=100, verbose_name='Carrera')
    email = models.EmailField(blank=True, null=True, verbose_name='Correo Electrónico')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    
    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering = ['nombre_completo']
    
    def __str__(self):
        return f"{self.nombre_completo} ({self.carnet_universitario})"


class Prestamo(models.Model):
    """Modelo para gestionar préstamos de libros y tesis"""
    
    TIPO_CHOICES = [
        ('SALA', 'En Sala (Deja Carnet Universitario)'),
        ('DOMICILIO', 'A Domicilio (Deja CI - Máximo 2 días)'),
    ]
    
    ESTADO_CHOICES = [
        ('VIGENTE', 'Vigente'),
        ('DEVUELTO', 'Devuelto'),
        ('ATRASADO', 'Atrasado'),
    ]
    
    # Relaciones
    activo = models.ForeignKey(
        ActivoBibliografico, 
        on_delete=models.CASCADE, 
        related_name='prestamos',
        verbose_name='Activo Bibliográfico'
    )
    estudiante = models.ForeignKey(
        Estudiante, 
        on_delete=models.CASCADE,
        related_name='prestamos',
        verbose_name='Estudiante'
    )
    usuario_prestamo = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='prestamos_realizados',
        verbose_name='Usuario que registró'
    )
    
    # Campos de préstamo
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Préstamo')
    fecha_prestamo = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Préstamo')
    fecha_devolucion_estimada = models.DateTimeField(verbose_name='Fecha de Devolución Estimada')
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Devolución Real')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='VIGENTE', verbose_name='Estado')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    
    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = ['-fecha_prestamo']
    
    def save(self, *args, **kwargs):
        """Calcular fecha de devolución automática según el tipo de préstamo"""
        if not self.pk:  # Solo al crear
            if self.tipo == 'DOMICILIO':
                # 2 días de plazo
                self.fecha_devolucion_estimada = timezone.now() + timedelta(days=2)
            else:
                # En sala: Se devuelve el mismo día (al final del día)
                self.fecha_devolucion_estimada = timezone.now().replace(hour=23, minute=59)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.estudiante.nombre_completo} - {self.activo.codigo_nuevo or 'S/C'}"
