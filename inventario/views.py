from rest_framework.permissions import AllowAny

# Endpoint público para IDs de activos prestados
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
@permission_classes([AllowAny])
def activos_prestados_publico(request):
    ids = list(Prestamo.objects.filter(estado='VIGENTE').values_list('activo_id', flat=True))
    return Response({'prestados': ids or []})
from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Case, When, Value, BooleanField
from django.utils import timezone
import traceback
import re
from .models import Libro, TrabajoGrado, ActivoBibliografico, Estudiante, Prestamo
from .serializers import (
    LibroSerializer, TrabajoGradoSerializer, ActivoSelectSerializer,
    EstudianteSerializer, PrestamoSerializer
)


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
        # 1. Obtener historial de Libros y Tesis
        historial_libros = list(Libro.history.all().order_by('-history_date')[:50])
        historial_tesis = list(TrabajoGrado.history.all().order_by('-history_date')[:50])

        # 2. Unificar y formatear
        data = []

        def formatear_registro(record, tipo, extra=None):
            accion = 'Modificado'
            if record.history_type == '+': accion = 'Creado'
            if record.history_type == '-': accion = 'Eliminado'
            # Campos comunes
            reg = {
                'history_id': record.history_id,
                'id_original': record.id,
                'titulo': record.titulo,
                'codigo': getattr(record, 'codigo_nuevo', None),
                'fecha': record.history_date.isoformat(),
                'usuario': str(record.history_user) if record.history_user else 'Sistema',
                'accion': accion,
                'tipo': tipo,
                'modelo': 'libro' if tipo == 'Libro' else 'tesis',
                'autor': getattr(record, 'autor', None),
                'anio': getattr(record, 'anio', None),
                'facultad': getattr(record, 'facultad', None),
                'estado': getattr(record, 'estado', None),
                'observaciones': getattr(record, 'observaciones', None),
                'ubicacion_seccion': getattr(record, 'ubicacion_seccion', None),
                'ubicacion_repisa': getattr(record, 'ubicacion_repisa', None),
                'fecha_registro': getattr(record, 'fecha_registro', None),
            }
            # Campos específicos de Libro
            if tipo == 'Libro':
                reg.update({
                    'materia': getattr(record, 'materia', None),
                    'editorial': getattr(record, 'editorial', None),
                    'edicion': getattr(record, 'edicion', None),
                    'codigo_seccion_full': getattr(record, 'codigo_seccion_full', None),
                    'orden_importacion': getattr(record, 'orden_importacion', None),
                })
            # Campos específicos de Tesis
            if tipo == 'Tesis':
                reg.update({
                    'modalidad': getattr(record, 'modalidad', None),
                    'tutor': getattr(record, 'tutor', None),
                    'carrera': getattr(record, 'carrera', None),
                })
            if extra:
                reg['estado_anterior'] = extra
            return reg

        def obtener_estado_anterior(hist_list):
            # Devuelve lista de registros, duplicando los 'Modificado' con su estado anterior
            resultado = []
            for idx, rec in enumerate(hist_list):
                tipo = 'Libro' if hasattr(rec, 'materia') else 'Tesis'
                # Si es modificación, buscar el registro anterior inmediato (mismo id_original)
                if rec.history_type == '~':
                    # Buscar el anterior con mismo id
                    prev = None
                    for siguiente in hist_list[idx+1:]:
                        if siguiente.id == rec.id:
                            prev = siguiente
                            break
                    # Agregar el registro modificado
                    resultado.append(formatear_registro(rec, tipo))
                    # Si hay anterior, agregarlo como 'Estado Anterior'
                    if prev:
                        resultado.append(formatear_registro(prev, tipo, extra={
                            'history_id': prev.history_id,
                            'id_original': prev.id,
                            'titulo': prev.titulo,
                            'codigo': getattr(prev, 'codigo_nuevo', None),
                            'fecha': prev.history_date.isoformat(),
                            'usuario': str(prev.history_user) if prev.history_user else 'Sistema',
                            'accion': 'Estado Anterior',
                            'tipo': tipo,
                            'modelo': 'libro' if tipo == 'Libro' else 'tesis'
                        }))
                else:
                    resultado.append(formatear_registro(rec, tipo))
            return resultado

        # Procesar ambos historiales
        data.extend(obtener_estado_anterior(historial_libros))
        data.extend(obtener_estado_anterior(historial_tesis))

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


class PerfilUsuarioView(APIView):
    """
    Vista para gestionar el perfil del usuario autenticado.
    Permite ver y actualizar datos personales y contraseña.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Devolver datos del usuario actual"""
        user = request.user
        data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        return Response(data)

    def patch(self, request):
        """Actualizar datos del usuario actual"""
        user = request.user
        data = request.data

        # Actualizar campos básicos
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']

        # Actualizar contraseña (solo si se envía y no está vacía)
        if 'password' in data and data['password']:
            user.set_password(data['password'])
            user.save()
            return Response({
                'mensaje': 'Perfil y contraseña actualizados. Vuelve a iniciar sesión.',
                'password_changed': True
            })
        
        user.save()
        return Response({
            'mensaje': 'Perfil actualizado correctamente',
            'password_changed': False
        })


class ActivoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de solo lectura para buscar activos bibliográficos (libros y tesis).
    Usada para el selector de préstamos.
    """
    queryset = ActivoBibliografico.objects.all()
    serializer_class = ActivoSelectSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'codigo_nuevo', 'autor']
    pagination_class = None


class EstudianteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar estudiantes.
    Permite crear, leer, actualizar y eliminar estudiantes.
    """
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre_completo', 'carnet_universitario', 'ci', 'carrera']
    pagination_class = None


class PrestamoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar préstamos de libros y tesis.
    Implementa reglas de negocio avanzadas:
    - Las tesis SOLO se pueden prestar para consulta en sala
    - Los libros se pueden prestar en sala o a domicilio
    - Auto-registro de estudiantes nuevos
    - Prevención de doble préstamo
    - Conversión automática de SALA → DOMICILIO para el mismo estudiante
    """
    queryset = Prestamo.objects.all().order_by('-fecha_prestamo')
    serializer_class = PrestamoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        'estudiante__nombre_completo', 
        'estudiante__carnet_universitario',
        'activo__titulo', 
        'activo__codigo_nuevo'
    ]
    filterset_fields = {
        'estado': ['exact'],
        'tipo': ['exact'],
    }
    pagination_class = None

    def create(self, request, *args, **kwargs):
        """
        Creación inteligente de préstamos con reglas de negocio avanzadas.
        """
        data = request.data.copy()
        
        # --- 1. AUTO-REGISTRO INTELIGENTE DE ESTUDIANTE ---
        estudiante_id = data.get('estudiante')
        
        # Si no viene ID, intentamos buscar por CI o crear nuevo
        if not estudiante_id:
            nombre = data.get('nuevo_nombre')
            ci = data.get('nuevo_ci')
            # Carrera ya no es obligatoria en el formulario, ponemos default
            carrera = data.get('nuevo_carrera', 'No especificada')
            
            if ci:
                # Buscamos si ya existe por CI (limpiamos espacios)
                ci_limpio = str(ci).strip()
                estudiante = Estudiante.objects.filter(ci=ci_limpio).first()
                
                if estudiante:
                    # ¡YA EXISTÍA! Usamos este
                    estudiante_id = estudiante.id
                elif nombre:
                    # NO EXISTE y tenemos nombre -> CREAR
                    estudiante = Estudiante.objects.create(
                        nombre_completo=nombre,
                        ci=ci_limpio,
                        carnet_universitario=ci_limpio,
                        carrera=carrera
                    )
                    estudiante_id = estudiante.id
                
                data['estudiante'] = estudiante_id
        
        # --- 2. REGLAS DE NEGOCIO: PREVENIR DOBLE PRÉSTAMO ---
        activo_id = data.get('activo')
        tipo_nuevo = data.get('tipo')
        
        # Buscar si el libro ya está prestado y vigente
        prestamo_actual = Prestamo.objects.filter(
            activo_id=activo_id,
            estado='VIGENTE'
        ).first()
        
        if prestamo_actual:
            # CASO ESPECIAL: ¿Es el mismo estudiante cambiando de SALA a DOMICILIO?
            es_mismo_estudiante = int(prestamo_actual.estudiante.id) == int(estudiante_id)
            es_cambio_sala_a_domicilio = prestamo_actual.tipo == 'SALA' and tipo_nuevo == 'DOMICILIO'
            
            if es_mismo_estudiante and es_cambio_sala_a_domicilio:
                # ✅ Cerrar automáticamente el préstamo en SALA
                prestamo_actual.estado = 'DEVUELTO'
                prestamo_actual.fecha_devolucion_real = timezone.now()
                obs_adicional = " [Auto-cerrado: Cambio a Domicilio]"
                prestamo_actual.observaciones = (prestamo_actual.observaciones or '') + obs_adicional
                prestamo_actual.save()
                # Permitir continuar con la creación del nuevo préstamo
            else:
                # Bloquear: El libro está ocupado por otro estudiante
                # Determinar el mensaje según el tipo de préstamo
                if prestamo_actual.tipo == 'SALA':
                    estado_texto = "está siendo usado en sala de lectura"
                else:
                    estado_texto = "fue prestado a domicilio"
                
                return Response(
                    {
                        "error": f"Libro no disponible: {estado_texto}",
                        "detalle": f"El libro '{prestamo_actual.activo.titulo}' {estado_texto}",
                        "tipo_prestamo": prestamo_actual.tipo,
                        "estudiante": prestamo_actual.estudiante.nombre_completo
                    },
                    status=400
                )
        
        # Continuar con la creación normal
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        """
        Validar reglas de negocio al crear un préstamo.
        REGLA CRÍTICA: Las tesis NO se pueden prestar a domicilio.
        """
        activo = serializer.validated_data['activo']
        tipo_prestamo = serializer.validated_data['tipo']

        # Validar: TESIS SOLO EN SALA
        if activo.tipo_activo == 'TESIS' and tipo_prestamo == 'DOMICILIO':
            raise ValidationError({
                "tipo": "Las Tesis NO se pueden prestar a domicilio. Solo consulta en Sala."
            })

        # Asignar usuario que registra el préstamo
        serializer.save(usuario_prestamo=self.request.user)

    @action(detail=True, methods=['post'])
    def devolver(self, request, pk=None):
        """
        Acción personalizada para marcar un libro como devuelto.
        """
        prestamo = self.get_object()
        
        if prestamo.estado == 'DEVUELTO':
            return Response(
                {'error': 'Este material ya fue devuelto'},
                status=400
            )
        
        prestamo.estado = 'DEVUELTO'
        prestamo.fecha_devolucion_real = timezone.now()
        prestamo.save()
        
        # Mensaje según el tipo de garantía
        if prestamo.tipo == 'SALA':
            mensaje = 'Material devuelto exitosamente. Entregar Carnet Universitario al estudiante.'
        else:
            mensaje = 'Material devuelto exitosamente. Entregar Cédula de Identidad al estudiante.'
        
        return Response({'mensaje': mensaje})
