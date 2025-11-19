from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Case, When, Value, BooleanField
import traceback
import re
from .models import Libro, TrabajoGrado
from .serializers import LibroSerializer, TrabajoGradoSerializer


class LibroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar libros.
    Permite búsqueda, filtros avanzados y ordenamiento.
    BÚSQUEDA OMNIPOTENTE: Busca en TODOS los campos de texto visibles en la tabla.
    ORDENAMIENTO NATURAL: Los códigos se ordenan numéricamente (S1-R1-0001 antes que S1-R1-0039)
    Los libros sin código van al final.
    """
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    
    # 🔍 BÚSQUEDA OMNIPOTENTE: Todos los campos de las 16 columnas
    search_fields = [
        'codigo_nuevo',         # Código Nuevo
        'codigo_antiguo',       # Código Antiguo
        'codigo_seccion_full',  # Código Sección
        'titulo',               # Título
        'autor',                # Autor
        'editorial',            # Editorial
        'edicion',              # Edición
        'facultad',             # Facultad
        'materia',              # Materia
        'ubicacion_seccion',    # Sección
        'ubicacion_repisa',     # Repisa
        'estado',               # Estado
        'observaciones'         # Observaciones
    ]
    
    filterset_fields = {
        'codigo_nuevo': ['exact', 'icontains'],
        'titulo': ['icontains'],
        'materia': ['icontains'],
        'facultad': ['icontains'],
        'editorial': ['icontains'],
        'ubicacion_seccion': ['exact'],
        'estado': ['exact'],
        'anio': ['exact'],
    }
    
    def list(self, request, *args, **kwargs):
        """
        Método personalizado de listado con ordenamiento inteligente en Python.
        Ordena los libros por código de sección de forma natural (numérica).
        """
        # 1. Aplicar filtros de búsqueda primero
        queryset = self.filter_queryset(self.get_queryset())
        
        # 2. Convertir a lista para ordenar en Python
        libros = list(queryset)

        # 3. Función de clave de ordenamiento inteligente
        def llave_ordenamiento(libro):
            codigo = libro.codigo_seccion_full
            if not codigo or codigo.strip() == '':
                # Sin código -> va al final (peso 1)
                return (1, [])
            
            # Extraer todos los números del código usando regex
            # Ej: "S1-R1-0039" -> [1, 1, 39]
            try:
                numeros = [int(n) for n in re.findall(r'\d+', codigo)]
                return (0, numeros)  # Con código -> va al principio (peso 0)
            except:
                return (1, [])  # Si falla, al final

        # 4. Ordenar en memoria usando Python (muy rápido para ~2000 registros)
        libros.sort(key=llave_ordenamiento)

        # 5. Serializar y devolver
        serializer = self.get_serializer(libros, many=True)
        return Response(serializer.data)
    ordering = ['-fecha_registro']


class TrabajoGradoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar trabajos de grado (tesis).
    Permite búsqueda, filtros avanzados y ordenamiento.
    BÚSQUEDA OMNIPOTENTE: Busca en TODOS los campos de texto visibles.
    ORDENAMIENTO NATURAL: Los códigos se ordenan numéricamente (ADM-0001 antes que ADM-0025)
    """
    queryset = TrabajoGrado.objects.all()
    serializer_class = TrabajoGradoSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    
    # 🔍 BÚSQUEDA OMNIPOTENTE: Todos los campos de tesis
    search_fields = [
        'codigo_nuevo',         # Código Nuevo
        'titulo',               # Título
        'autor',                # Autor (Estudiante)
        'tutor',                # Tutor
        'carrera',              # Carrera
        'facultad',             # Facultad (heredado de base)
        'modalidad',            # Modalidad
        'ubicacion_seccion',    # Sección
        'ubicacion_repisa',     # Repisa
        'estado',               # Estado
        'observaciones'         # Observaciones
    ]
    
    filterset_fields = {
        'codigo_nuevo': ['exact', 'icontains'],
        'titulo': ['icontains'],
        'autor': ['icontains'],
        'carrera': ['icontains'],
        'tutor': ['icontains'],
        'modalidad': ['exact'],
        'estado': ['exact'],
        'facultad': ['icontains'],
    }
    
    def list(self, request, *args, **kwargs):
        """
        Método personalizado de listado con ordenamiento inteligente en Python.
        Ordena las tesis por código (ADM-0001, ADM-0002, CPU-001, etc.) de forma natural.
        """
        # 1. Aplicar filtros de búsqueda primero
        queryset = self.filter_queryset(self.get_queryset())
        
        # 2. Convertir a lista para ordenar en Python
        tesis = list(queryset)

        # 3. Función de clave de ordenamiento inteligente para tesis
        def llave_ordenamiento_tesis(tesis_item):
            codigo = tesis_item.codigo_nuevo
            if not codigo or codigo.strip() == '':
                # Sin código -> va al final (peso 1)
                return (1, '', [])
            
            # Extraer prefijo (letras) y números
            # Ej: "ADM-0025" -> prefijo="ADM", numeros=[25]
            try:
                # Extraer el prefijo de letras
                match = re.match(r'([A-Z]+)', codigo.upper())
                prefijo = match.group(1) if match else ''
                
                # Extraer números
                numeros = [int(n) for n in re.findall(r'\d+', codigo)]
                
                return (0, prefijo, numeros)  # Con código -> va al principio (peso 0)
            except:
                return (1, '', [])  # Si falla, al final

        # 4. Ordenar en memoria usando Python
        tesis.sort(key=llave_ordenamiento_tesis)

        # 5. Serializar y devolver
        serializer = self.get_serializer(tesis, many=True)
        return Response(serializer.data)


class DashboardStatsView(APIView):
    """
    Vista para obtener estadísticas del dashboard.
    Retorna: total de libros, tesis, distribución por estado y últimos agregados.
    """
    def get(self, request):
        try:
            # 1. Conteos Totales (Esto casi nunca falla)
            total_libros = Libro.objects.count()
            total_tesis = TrabajoGrado.objects.count()
            
            # 2. CÁLCULO DE ATENCIÓN (SUMA LIBROS + TESIS)
            # Contamos 'MALO' y 'EN REPARACION' en ambos modelos
            malos_libros = Libro.objects.filter(estado__in=['MALO', 'EN REPARACION']).count()
            malos_tesis = TrabajoGrado.objects.filter(estado__in=['MALO', 'EN REPARACION']).count()
            total_atencion = malos_libros + malos_tesis  # CORRECCIÓN: 12 + 2 = 14
            
            # 3. Estados de Libros (Con manejo de errores por si acaso)
            try:
                estados_raw = Libro.objects.values('estado').annotate(total=Count('estado'))
                libros_por_estado = {str(item['estado']): item['total'] for item in estados_raw}
            except Exception:
                libros_por_estado = {'MALO': 0}  # Fallback seguro

            # 4. Últimos Agregados (Aquí suele estar el error)
            ultimos = []
            try:
                # Usamos order_by('-fecha_registro') que es estándar y seguro
                recent_libros = Libro.objects.all().order_by('-fecha_registro')[:5]
                recent_tesis = TrabajoGrado.objects.all().order_by('-fecha_registro')[:5]

                for l in recent_libros:
                    fecha = l.fecha_registro.isoformat() if l.fecha_registro else ""
                    ultimos.append({
                        'id': l.id, 
                        'titulo': str(l.titulo), 
                        'codigo_nuevo': str(l.codigo_nuevo or 'S/C'), 
                        'estado': str(l.estado), 
                        'fecha': fecha, 
                        'tipo': 'Libro'
                    })

                for t in recent_tesis:
                    fecha = t.fecha_registro.isoformat() if t.fecha_registro else ""
                    ultimos.append({
                        'id': t.id, 
                        'titulo': str(t.titulo), 
                        'codigo_nuevo': str(t.codigo_nuevo or 'S/C'), 
                        'estado': str(t.estado), 
                        'fecha': fecha, 
                        'tipo': 'Tesis'
                    })
                
                # Ordenamos la lista combinada por fecha (descendente)
                ultimos.sort(key=lambda x: x['fecha'], reverse=True)
                
            except Exception as e:
                print(f"⚠️ Error procesando últimos: {e}")
                # Si falla, enviamos lista vacía pero NO rompemos todo el dashboard
                ultimos = []

            data = {
                "total_libros": total_libros,
                "total_tesis": total_tesis,
                "requieren_atencion": total_atencion,  # Enviamos el total sumado (libros + tesis)
                "libros_por_estado": libros_por_estado,
                "ultimos_agregados": ultimos[:5]  # Solo los top 5
            }
            
            return Response(data)
            
        except Exception as e:
            # Error catastrófico (DB caída, etc.)
            print(f"\n🔴 ERROR CRÍTICO DASHBOARD: {str(e)}")
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


class SiguienteCodigoView(APIView):
    """Vista para sugerir el siguiente código disponible (para libros o tesis)"""
    def get(self, request):
        tipo = request.query_params.get('tipo', 'libros')
        prefijo = request.query_params.get('prefijo', '').strip().upper()
        
        if not prefijo:
            return Response({'siguiente': ''})

        if tipo == 'libros':
            # Lógica para Libros (codigo_seccion_full: S1-R1-XXXX)
            libros = Libro.objects.filter(codigo_seccion_full__istartswith=prefijo)
            
            if not libros.exists():
                return Response({'siguiente': f"{prefijo}-0001"})

            max_num = 0
            for libro in libros:
                if libro.codigo_seccion_full:
                    try:
                        partes = libro.codigo_seccion_full.split('-')
                        numero = int(partes[-1])
                        if numero > max_num:
                            max_num = numero
                    except (ValueError, IndexError):
                        continue
            
            siguiente_num = str(max_num + 1).zfill(4)
            return Response({'siguiente': f"{prefijo}-{siguiente_num}"})
            
        else:
            # Lógica para Tesis (codigo_nuevo: ADM-0025, CPU-001)
            # Normalizar prefijo (quitar guion si lo escribió)
            clean_prefix = prefijo.rstrip('-')
            tesis_list = TrabajoGrado.objects.filter(codigo_nuevo__istartswith=clean_prefix)
            
            if not tesis_list.exists():
                return Response({'siguiente': f"{clean_prefix}-0001"})

            max_num = 0
            padding = 4  # Por defecto 4 dígitos (ADM-0001)
            
            for tesis in tesis_list:
                if tesis.codigo_nuevo:
                    try:
                        # Extraer el último grupo de números
                        numeros = re.findall(r'\d+', tesis.codigo_nuevo)
                        if numeros:
                            num = int(numeros[-1])
                            if num > max_num:
                                max_num = num
                                # Detectar padding (3 o 4 dígitos)
                                len_num_str = len(numeros[-1])
                                padding = max(3, len_num_str)
                    except:
                        continue
            
            siguiente_num = str(max_num + 1).zfill(padding)
            return Response({'siguiente': f"{clean_prefix}-{siguiente_num}"})


class ListaSeccionesView(APIView):
    """Vista para obtener todas las secciones/prefijos únicos disponibles (para libros o tesis)"""
    def get(self, request):
        tipo = request.query_params.get('tipo', 'libros')
        secciones = set()
        
        if tipo == 'libros':
            # Para libros: extraer "S1-R1" de "S1-R1-0001"
            codigos = Libro.objects.exclude(codigo_seccion_full__isnull=True).exclude(codigo_seccion_full='').values_list('codigo_seccion_full', flat=True)
            for c in codigos:
                if c:
                    # Unimos todo menos la última parte numérica
                    partes = c.split('-')
                    if len(partes) >= 2:
                        prefijo = "-".join(partes[:-1])  # S1-R1
                        secciones.add(prefijo)
        else:
            # Para tesis: extraer "ADM" de "ADM-0025"
            codigos = TrabajoGrado.objects.exclude(codigo_nuevo__isnull=True).exclude(codigo_nuevo='').values_list('codigo_nuevo', flat=True)
            for c in codigos:
                if c:
                    # Separar letras de números usando regex
                    match = re.match(r'([A-Z]+)', c.upper())
                    if match:
                        secciones.add(match.group(1))
                    else:
                        # Fallback: usar la parte antes del guion
                        partes = c.split('-')
                        if partes:
                            secciones.add(partes[0].upper())
        
        return Response(sorted(list(secciones)))
