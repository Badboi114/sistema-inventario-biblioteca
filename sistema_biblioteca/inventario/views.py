from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from .models import Libro, TrabajoGrado
from .serializers import LibroSerializer, TrabajoGradoSerializer


class LibroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar libros.
    Permite búsqueda y ordenamiento.
    """
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'codigo_nuevo', 'materia']
    ordering_fields = ['titulo', 'fecha_creacion', 'codigo_nuevo']
    ordering = ['-fecha_creacion']


class TrabajoGradoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar trabajos de grado (tesis).
    Permite búsqueda y ordenamiento.
    """
    queryset = TrabajoGrado.objects.all()
    serializer_class = TrabajoGradoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'autor', 'tutor']
    ordering_fields = ['titulo', 'fecha_creacion', 'fecha_presentacion']
    ordering = ['-fecha_creacion']


class DashboardStatsView(APIView):
    """
    Vista para obtener estadísticas del dashboard.
    Retorna: total de libros, tesis, distribución por estado y últimos agregados.
    """
    def get(self, request):
        # Conteo total
        total_libros = Libro.objects.count()
        total_tesis = TrabajoGrado.objects.count()
        
        # Libros por estado
        libros_por_estado = Libro.objects.values('estado').annotate(
            cantidad=Count('id')
        ).order_by('estado')
        
        # Convertir a formato más amigable
        estado_dict = {item['estado']: item['cantidad'] for item in libros_por_estado}
        
        # Últimos 5 agregados (tanto libros como tesis)
        ultimos_libros = Libro.objects.order_by('-fecha_creacion')[:5]
        ultimos_tesis = TrabajoGrado.objects.order_by('-fecha_creacion')[:5]
        
        ultimos_agregados = {
            'libros': LibroSerializer(ultimos_libros, many=True).data,
            'tesis': TrabajoGradoSerializer(ultimos_tesis, many=True).data,
        }
        
        return Response({
            'total_libros': total_libros,
            'total_tesis': total_tesis,
            'libros_por_estado': estado_dict,
            'ultimos_agregados': ultimos_agregados,
        })
