import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from inventario.models import Libro, TrabajoGrado
from django.db import transaction


class Command(BaseCommand):
    help = 'Importar TODO el contenido del Excel fila por fila (Modo Espejo)'

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

        print(f"Procesando hoja completa con {len(df)} filas...")
        creados = 0

        # Usamos transaction para velocidad
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # 1. VALIDACIÓN MÍNIMA: Si no hay título, asumimos que es una fila vacía del Excel
                    titulo = str(row.get('TITULO', '')).strip()
                    if not titulo or titulo.lower() == 'nan':
                        continue

                    # 2. Preparar Datos
                    raw_codigo = str(row.get('CODIGO NUEVO', '')).strip()
                    # Si el código es 'nan' o vacío, lo dejamos como None (vacío real)
                    codigo = None if (not raw_codigo or raw_codigo.lower() == 'nan') else raw_codigo

                    # Mapeo común
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
                    }

                    if tipo == 'libro':
                        # MODO ESPEJO: Crear SIEMPRE (sin importar duplicados)
                        Libro.objects.create(codigo_nuevo=codigo, **defaults)
                        creados += 1

                    elif tipo == 'tesis':
                        # Lógica Tesis
                        defaults_tesis = {
                            'titulo': titulo,
                            'autor': str(row.get('ESTUDIANTE', '')).strip(),
                            'tutor': str(row.get('TUTOR', '')).strip(),
                            'modalidad': str(row.get('MODALIDAD', '')).strip(),
                            'carrera': str(row.get('CARRERA', '')).strip(),
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

        self.stdout.write(self.style.SUCCESS(f'✅ CARGA COMPLETA: Se procesaron {creados} registros válidos.'))

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
