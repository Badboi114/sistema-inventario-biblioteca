import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from inventario.models import Libro, TrabajoGrado
from django.db import transaction
from django.db.models import Max


class Command(BaseCommand):
    help = 'Importar manteniendo el orden exacto y secuencial entre archivos'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str)
        parser.add_argument('tipo', type=str, choices=['libro', 'tesis'])
        parser.add_argument('--hoja', type=str, required=False)

    def handle(self, *args, **options):
        archivo = options['archivo']
        tipo = options['tipo']
        hoja = options.get('hoja')

        try:
            if archivo.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo, sheet_name=hoja if hoja else 0)
        except Exception as e:
            raise CommandError(f'Error: {e}')

        df.columns = df.columns.str.strip().str.upper()
        df = df.fillna('')

        print(f"Procesando {len(df)} filas...")
        
        # 🎯 CORRECCIÓN MAESTRA: Obtener el último orden usado
        if tipo == 'libro':
            max_order = Libro.objects.aggregate(Max('orden_importacion'))['orden_importacion__max']
            start_index = (max_order + 1) if max_order is not None else 0
            print(f"📊 Orden inicial: {start_index}")
        else:
            start_index = 0

        creados = 0
        omitidos = 0
        numeros_procesados_tesis = set()

        with transaction.atomic():
            for i, (index, row) in enumerate(df.iterrows()):
                try:
                    # Calculamos el orden absoluto desde el inicio de todos los libros
                    orden_real = start_index + i

                    # 1. VALIDACIÓN MÍNIMA: Si no hay título, asumimos que es una fila vacía del Excel
                    titulo = str(row.get('TITULO', '')).strip()
                    if not titulo or titulo.lower() == 'nan':
                        continue

                    # ==========================================
                    # LOGICA LIBROS (INTOCABLE - MODO ESPEJO)
                    # ==========================================
                    if tipo == 'libro':
                        # 2. Preparar Datos
                        raw_codigo = str(row.get('CODIGO NUEVO', '')).strip()
                        codigo = None if (not raw_codigo or raw_codigo.lower() == 'nan') else raw_codigo

                        defaults = {
                            'titulo': titulo,
                            'autor': str(row.get('AUTOR', '')).strip(),
                            'editorial': str(row.get('EDITORIAL', '')).strip(),
                            'edicion': str(row.get('EDICIÓN', '')).strip(),
                            'anio': self.parse_anio(row.get('AÑO')),
                            'facultad': str(row.get('FACULTAD', '')).strip(),
                            'materia': str(row.get('MATERIA', '')).strip(),
                            'codigo_antiguo': str(row.get('CODIGO ANTIGUO', '')).strip(),
                            'codigo_seccion_full': str(row.get('CODIGO DE SECCION', '')).strip(),
                            'ubicacion_seccion': str(row.get('SECCIÓN', '')).strip(),
                            'ubicacion_repisa': str(row.get('REPISA', '')).strip(),
                            'estado': self.normalizar_estado(str(row.get('ESTADO', 'REGULAR'))),
                            'observaciones': str(row.get('OBSERVACIONES', '')).strip(),
                            'orden_importacion': orden_real,  # 🎯 Orden secuencial absoluto
                        }
                        
                        # MODO ESPEJO: Crear SIEMPRE (sin importar duplicados)
                        Libro.objects.create(codigo_nuevo=codigo, **defaults)
                        creados += 1

                    # ==========================================
                    # LOGICA TESIS (ESTRICTA - SOLO N° 1-599 ÚNICOS)
                    # ==========================================
                    elif tipo == 'tesis':
                        # FILTRO ESTRICTO: Debe tener número válido en columna N°
                        raw_n = str(row.get('N°', row.get('Nº', ''))).strip()
                        
                        # Si no tiene número válido, OMITIR
                        if not raw_n or raw_n.lower() == 'nan':
                            omitidos += 1
                            continue
                        
                        # Verificar que sea numérico y esté en rango 1-599
                        try:
                            n = int(float(raw_n))
                            if n < 1 or n > 599:
                                omitidos += 1
                                continue
                            
                            # NO REPETIR NÚMEROS (garantiza máximo 599 únicos)
                            if n in numeros_procesados_tesis:
                                omitidos += 1
                                continue
                            
                            numeros_procesados_tesis.add(n)
                            
                        except (ValueError, TypeError):
                            omitidos += 1
                            continue
                        
                        # Preparar código
                        raw_codigo = str(row.get('CODIGO NUEVO', '')).strip()
                        if not raw_codigo:
                            raw_codigo = str(row.get('CODIGO NUEVO ', '')).strip()
                        codigo = None if (not raw_codigo or raw_codigo.lower() == 'nan') else raw_codigo

                        # Preparar datos de tesis
                        defaults_tesis = {
                            'titulo': titulo,
                            'autor': str(row.get('ESTUDIANTE', '')).strip(),
                            'tutor': str(row.get('TUTOR', '')).strip(),
                            'modalidad': str(row.get('MODALIDAD', '')).strip(),
                            'carrera': str(row.get('CARRERA', row.get('CARRERA ', ''))).strip(),
                            'facultad': str(row.get('FACULTAD', '')).strip(),
                            'anio': self.parse_anio(row.get('AÑO')),
                            'estado': self.normalizar_estado(str(row.get('ESTADO', 'REGULAR'))),
                        }
                        
                        if codigo:
                            TrabajoGrado.objects.update_or_create(codigo_nuevo=codigo, defaults=defaults_tesis)
                        else:
                            TrabajoGrado.objects.create(codigo_nuevo=None, **defaults_tesis)
                        creados += 1

                except Exception as e:
                    print(f"Error fila {index}: {e}")

        self.stdout.write(self.style.SUCCESS(f'✅ CARGA COMPLETA: Se procesaron {creados} registros válidos. Omitidos: {omitidos}. Rango de orden: {start_index} al {start_index + creados}'))

    def parse_anio(self, value):
        try:
            return int(float(value))
        except:
            return None

    def normalizar_estado(self, estado):
        estado_upper = estado.upper()
        if 'BUEN' in estado_upper:
            return 'BUENO'
        elif 'MAL' in estado_upper:
            return 'MALO'
        elif 'REGULAR' in estado_upper:
            return 'REGULAR'
        else:
            return 'REGULAR'
