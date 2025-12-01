from rest_framework import serializers
from .models import Libro, TrabajoGrado, ActivoBibliografico, Estudiante, Prestamo


class LibroSerializer(serializers.ModelSerializer):
    """Serializer completo para Libros"""
    class Meta:
        model = Libro
        fields = '__all__'


class TrabajoGradoSerializer(serializers.ModelSerializer):
    """Serializer completo para Trabajos de Grado"""
    class Meta:
        model = TrabajoGrado
        fields = '__all__'


class LibroSearchSerializer(serializers.ModelSerializer):
    """Serializer ligero para búsquedas rápidas"""
    class Meta:
        model = Libro
        fields = ['id', 'titulo', 'codigo_nuevo', 'ubicacion_seccion', 'ubicacion_repisa', 'estado']


class ActivoSelectSerializer(serializers.ModelSerializer):
    """Serializer para el selector de préstamos (libros y tesis)"""
    tipo = serializers.ReadOnlyField(source='tipo_activo')
    
    class Meta:
        model = ActivoBibliografico
        fields = ['id', 'titulo', 'codigo_nuevo', 'tipo', 'autor', 'estado']


class EstudianteSerializer(serializers.ModelSerializer):
    """Serializer completo para Estudiantes"""
    prestamos_activos = serializers.SerializerMethodField()
    
    class Meta:
        model = Estudiante
        fields = '__all__'
    
    def get_prestamos_activos(self, obj):
        """Cuenta cuántos préstamos activos tiene el estudiante"""
        return obj.prestamos.filter(estado='VIGENTE').count()


class PrestamoSerializer(serializers.ModelSerializer):
    """Serializer completo para Préstamos"""
    # Campos de solo lectura para mostrar información relacionada
    activo_titulo = serializers.CharField(source='activo.titulo', read_only=True)
    activo_codigo = serializers.CharField(source='activo.codigo_nuevo', read_only=True)
    activo_tipo = serializers.CharField(source='activo.tipo_activo', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.nombre_completo', read_only=True)
    estudiante_carnet = serializers.CharField(source='estudiante.carnet_universitario', read_only=True)
    estudiante_carrera = serializers.CharField(source='estudiante.carrera', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario_prestamo.username', read_only=True)
    
    class Meta:
        model = Prestamo
        fields = '__all__'
        read_only_fields = ['usuario_prestamo', 'fecha_prestamo', 'fecha_devolucion_estimada']
