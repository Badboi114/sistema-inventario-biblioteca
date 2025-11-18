from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
import traceback
from .models import Libro, TrabajoGrado
from .serializers import LibroSerializer, TrabajoGradoSerializer


class LibroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar libros.
    Permite búsqueda y ordenamiento.
    """
    queryset = Libro.objects.all().order_by('-fecha_registro')
    serializer_class = LibroSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'codigo_nuevo', 'materia', 'autor']
    ordering_fields = ['titulo', 'fecha_registro', 'codigo_nuevo', 'anio', 'estado']
    ordering = ['-fecha_registro']


class TrabajoGradoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar trabajos de grado (tesis).
    Permite búsqueda y ordenamiento.
    """
    queryset = TrabajoGrado.objects.all().order_by('-fecha_registro')
    serializer_class = TrabajoGradoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'autor', 'tutor', 'carrera']
    ordering_fields = ['titulo', 'fecha_registro', 'anio', 'modalidad']
    ordering = ['-fecha_registro']


class DashboardStatsView(APIView):
    """
    Vista para obtener estadísticas del dashboard.
    Retorna: total de libros, tesis, distribución por estado y últimos agregados.
    """
    def get(self, request):
        try:
            # Conteo total
            total_libros = Libro.objects.count()
            total_tesis = TrabajoGrado.objects.count()
            
            # Libros por estado - convertir a diccionario simple
            libros_por_estado_raw = Libro.objects.values('estado').annotate(
                cantidad=Count('id')
            ).order_by('estado')
            
            estado_dict = {str(item['estado']): item['cantidad'] for item in libros_por_estado_raw}
            
            # Últimos 5 libros agregados - serialización manual
            ultimos_libros = Libro.objects.all().order_by('-fecha_registro')[:5]
            ultimos_libros_data = []
            for libro in ultimos_libros:
                ultimos_libros_data.append({
                    'id': libro.id,
                    'titulo': str(libro.titulo),
                    'codigo_nuevo': str(libro.codigo_nuevo),
                    'estado': str(libro.estado),
                    'fecha_creacion': libro.fecha_registro.isoformat() if libro.fecha_registro else None
                })
            
            # Últimas 5 tesis agregadas
            ultimos_tesis = TrabajoGrado.objects.all().order_by('-fecha_registro')[:5]
            ultimos_tesis_data = []
            for tesis in ultimos_tesis:
                ultimos_tesis_data.append({
                    'id': tesis.id,
                    'titulo': str(tesis.titulo),
                    'codigo_nuevo': str(tesis.codigo_nuevo),
                    'estado': str(tesis.estado),
                    'fecha_creacion': tesis.fecha_registro.isoformat() if tesis.fecha_registro else None
                })
            
            ultimos_agregados = {
                'libros': ultimos_libros_data,
                'tesis': ultimos_tesis_data,
            }
            
            data = {
                'total_libros': total_libros,
                'total_tesis': total_tesis,
                'libros_por_estado': estado_dict,
                'ultimos_agregados': ultimos_agregados,
            }
            
            return Response(data)
            
        except Exception as e:
            # Imprime el error en la consola de Django
            print(f"\n🔴 ERROR CRÍTICO EN DASHBOARD: {str(e)}")
            traceback.print_exc()
            return Response(
                {"error": "Error interno del servidor", "detalle": str(e)}, 
                status=500
            )
