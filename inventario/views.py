from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
import traceback
from .models import Libro, TrabajoGrado
from .serializers import LibroSerializer, TrabajoGradoSerializer


class LibroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar libros.
    Permite búsqueda, filtros avanzados y ordenamiento.
    """
    queryset = Libro.objects.all().order_by('-fecha_registro')
    serializer_class = LibroSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['titulo', 'codigo_nuevo', 'materia', 'autor']
    filterset_fields = {
        'codigo_nuevo': ['exact', 'icontains'],
        'titulo': ['icontains'],
        'materia': ['icontains'],
        'ubicacion_seccion': ['exact'],
        'estado': ['exact'],
        'anio': ['exact'],
    }
    ordering_fields = ['titulo', 'fecha_registro', 'codigo_nuevo', 'anio', 'estado']
    ordering = ['-fecha_registro']


class TrabajoGradoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar trabajos de grado (tesis).
    Permite búsqueda, filtros avanzados y ordenamiento.
    """
    queryset = TrabajoGrado.objects.all().order_by('-fecha_registro')
    serializer_class = TrabajoGradoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['titulo', 'autor', 'tutor', 'carrera', 'codigo_nuevo']
    filterset_fields = {
        'codigo_nuevo': ['exact', 'icontains'],
        'titulo': ['icontains'],
        'autor': ['icontains'],
        'carrera': ['icontains'],
        'tutor': ['icontains'],
        'modalidad': ['exact'],
        'ubicacion_seccion': ['exact'],
        'estado': ['exact'],
    }
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


class HistorialView(APIView):
    """Vista para obtener el historial de auditoría de libros y tesis"""
    def get(self, request):
        # 1. Obtener historial de Libros
        historial_libros = Libro.history.all().order_by('-history_date')[:50]  # Últimos 50
        
        # 2. Obtener historial de Tesis
        historial_tesis = TrabajoGrado.history.all().order_by('-history_date')[:50]
        
        # 3. Unificar y formatear
        data = []
        
        def formatear_registro(record, tipo):
            accion = 'Modificado'
            if record.history_type == '+': accion = 'Creado'
            if record.history_type == '-': accion = 'Eliminado'
            
            return {
                'history_id': record.history_id,
                'id_original': record.id,
                'titulo': record.titulo,
                'codigo': record.codigo_nuevo,
                'fecha': record.history_date.isoformat(),
                'usuario': str(record.history_user) if record.history_user else 'Sistema',
                'accion': accion,
                'tipo': tipo,
                'modelo': 'libro' if tipo == 'Libro' else 'tesis'
            }

        for h in historial_libros: data.append(formatear_registro(h, 'Libro'))
        for h in historial_tesis: data.append(formatear_registro(h, 'Tesis'))
        
        # Ordenar mezcla por fecha descendente
        data.sort(key=lambda x: x['fecha'], reverse=True)
        
        return Response(data)


class RestaurarRegistroView(APIView):
    """Vista para restaurar un registro desde el historial"""
    def post(self, request, modelo, history_id):
        try:
            # Determinar modelo
            ModelHist = Libro.history if modelo == 'libro' else TrabajoGrado.history
            
            # Buscar el registro histórico
            registro_historico = ModelHist.get(history_id=history_id)
            
            # Restaurar (La magia de simple_history)
            # Esto recupera la instancia tal cual estaba en ese momento
            instancia = registro_historico.instance
            
            # Guardamos para "revivirlo" en la tabla principal
            instancia.save()
            
            return Response({"mensaje": "Restaurado exitosamente"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
