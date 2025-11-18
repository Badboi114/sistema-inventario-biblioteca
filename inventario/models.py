from django.db import models
from simple_history.models import HistoricalRecords


class ActivoBibliografico(models.Model):
    """Clase base para todos los activos bibliográficos de la biblioteca"""
    
    ESTADO_CHOICES = [
        ('BUENO', 'Bueno'),
        ('REGULAR', 'Regular'),
        ('MALO', 'Malo'),
        ('EN REPARACION', 'En Reparación'),
    ]
    
    codigo_nuevo = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='Código Nuevo')
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
    
    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
    
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
