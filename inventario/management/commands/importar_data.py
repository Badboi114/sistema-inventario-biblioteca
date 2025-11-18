import pandas as pd
from django.core.management.base import BaseCommand
from inventario.models import Libro, TrabajoGrado


class Command(BaseCommand):
    help = 'Importa datos desde archivos CSV/Excel para libros o tesis'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta del archivo CSV o Excel a importar')
        parser.add_argument('tipo', type=str, choices=['libro', 'tesis'], help='Tipo de datos: libro o tesis')
        parser.add_argument('--hoja', type=str, default=None, help='Nombre de la hoja de Excel a importar (opcional)')

    def handle(self, *args, **options):
        archivo = options['archivo']
        tipo = options['tipo']
        hoja = options.get('hoja')

        self.stdout.write(self.style.WARNING(f'Iniciando importación de {tipo}s desde {archivo}...'))
        if hoja:
            self.stdout.write(self.style.WARNING(f'Leyendo hoja: {hoja}'))

        try:
            # Leer el archivo con pandas
            if archivo.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                # Si es Excel y se especifica una hoja, leerla
                if hoja:
                    df = pd.read_excel(archivo, sheet_name=hoja)
                else:
                    df = pd.read_excel(archivo)

            # NORMALIZAR COLUMNAS: eliminar espacios y convertir a mayúsculas
            df.columns = df.columns.str.strip().str.upper()
            self.stdout.write(f'Columnas detectadas: {list(df.columns[:10])}...')

            # Rellenar valores NaN con cadenas vacías
            df = df.fillna('')

            registros_importados = 0

            if tipo == 'libro':
                registros_importados = self.importar_libros(df)
            elif tipo == 'tesis':
                registros_importados = self.importar_tesis(df)

            self.stdout.write(self.style.SUCCESS(f'✓ Importación completada: {registros_importados} registros de {tipo}s importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la importación: {str(e)}'))

    def importar_libros(self, df):
        """Importa registros de libros desde el DataFrame"""
        contador = 0
        total = len(df)

        for index, row in df.iterrows():
            try:
                # Mostrar progreso cada 50 filas
                if (index + 1) % 50 == 0:
                    self.stdout.write(f'  Procesando fila {index + 1}/{total}...')

                # Obtener código nuevo (ya normalizado sin espacios)
                codigo = str(row.get('CODIGO NUEVO', '')).strip()
                if not codigo:
                    continue

                # Convertir año a entero, manejar errores
                anio = None
                if row.get('AÑO', '') != '':
                    try:
                        anio = int(float(row['AÑO']))
                    except (ValueError, TypeError):
                        anio = None

                # Crear o actualizar el libro
                libro, created = Libro.objects.update_or_create(
                    codigo_nuevo=codigo,
                    defaults={
                        'titulo': str(row.get('TITULO', '')).strip(),
                        'autor': str(row.get('AUTOR', '')).strip(),
                        'editorial': str(row.get('EDITORIAL', '')).strip(),
                        'edicion': str(row.get('EDICIÓN', '') or row.get('EDICION', '')).strip(),
                        'anio': anio,
                        'materia': str(row.get('MATERIA', '')).strip(),
                        'codigo_seccion_full': str(row.get('CODIGO DE SECCION', '')).strip(),
                        'ubicacion_seccion': str(row.get('SECCIÓN', '') or row.get('SECCION', '')).strip(),
                        'ubicacion_repisa': str(row.get('REPISA', '')).strip(),
                        'estado': str(row.get('ESTADO', 'BUENO')).strip().upper(),
                        'observaciones': str(row.get('OBSERVACIONES', '')).strip(),
                    }
                )
                contador += 1

                if created:
                    self.stdout.write(f'  + Libro creado: {libro.codigo_nuevo} - {libro.titulo[:50]}')
                else:
                    self.stdout.write(f'  ↻ Libro actualizado: {libro.codigo_nuevo} - {libro.titulo[:50]}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error en fila {index + 1}: {str(e)}'))

        return contador

    def importar_tesis(self, df):
        """Importa registros de trabajos de grado/tesis desde el DataFrame"""
        contador = 0
        total = len(df)

        for index, row in df.iterrows():
            try:
                # Mostrar progreso cada 50 filas
                if (index + 1) % 50 == 0:
                    self.stdout.write(f'  Procesando fila {index + 1}/{total}...')

                # Obtener código nuevo (ya normalizado sin espacios)
                codigo = str(row.get('CODIGO NUEVO', '')).strip()
                if not codigo:
                    continue

                # Convertir año a entero, manejar errores
                anio = None
                if row.get('AÑO', '') != '':
                    try:
                        anio = int(float(row['AÑO']))
                    except (ValueError, TypeError):
                        anio = None

                # Obtener carrera (ya normalizada)
                carrera = str(row.get('CARRERA', '')).strip()

                # Crear o actualizar el trabajo de grado
                tesis, created = TrabajoGrado.objects.update_or_create(
                    codigo_nuevo=codigo,
                    defaults={
                        'titulo': str(row.get('TITULO', '')).strip(),
                        'autor': str(row.get('ESTUDIANTE', '')).strip(),
                        'tutor': str(row.get('TUTOR', '')).strip(),
                        'modalidad': str(row.get('MODALIDAD', 'TESIS')).strip().upper(),
                        'carrera': carrera,
                        'facultad': str(row.get('FACULTAD', '')).strip(),
                        'anio': anio,
                        'estado': str(row.get('ESTADO', 'BUENO')).strip().upper(),
                        'ubicacion_seccion': str(row.get('SECCIÓN', '') or row.get('SECCION', '')).strip(),
                        'ubicacion_repisa': str(row.get('REPISA', '')).strip(),
                        'observaciones': str(row.get('OBSERVACIONES', '')).strip(),
                    }
                )
                contador += 1

                if created:
                    self.stdout.write(f'  + Tesis creada: {tesis.codigo_nuevo} - {tesis.titulo[:50]}')
                else:
                    self.stdout.write(f'  ↻ Tesis actualizada: {tesis.codigo_nuevo} - {tesis.titulo[:50]}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error en fila {index + 1}: {str(e)}'))

        return contador
