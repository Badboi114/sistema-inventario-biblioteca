from rest_framework import serializers
from .models import Libro, TrabajoGrado


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
