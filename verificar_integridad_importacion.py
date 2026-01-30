import os
import sys
import django
import pandas as pd
from collections import Counter

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Libro, TrabajoGrado

def limpiar_valor(valor):
    if pd.isna(valor):
        return ''
    valor_str = str(valor).strip()
    if valor_str.lower() in ['nan', 'none', '']:
        return ''
    return valor_str

# Leer Excel
archivo_excel = r'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'
excel_file = pd.ExcelFile(archivo_excel)
df_libros = pd.read_excel(archivo_excel, sheet_name='LISTA DE LIBROS ACADEMICOS')
df_lectura = pd.read_excel(archivo_excel, sheet_name='LIBROS DE LECTURA')
df_tesis = pd.read_excel(archivo_excel, sheet_name='LISTA DE PROYECTOS DE GRADO (2)')

# Unificar libros
libros_excel = pd.concat([df_libros, df_lectura], ignore_index=True)
libros_excel_codigos = set()
libros_excel_titulos = set()
for idx, row in libros_excel.iterrows():
    codigo = limpiar_valor(row.get('CODIGO NUEVO', ''))
    if not codigo:
        codigo = limpiar_valor(row.get('CODIGO NUEVO ', ''))
    if not codigo:
        codigo = f'SIN-LIB-{idx+1:04d}'
    libros_excel_codigos.add(codigo)
    libros_excel_titulos.add(limpiar_valor(row.get('TITULO', '')).strip().lower())

# Tesis
tesis_excel_codigos = set()
tesis_excel_titulos = set()
for idx, row in df_tesis.iterrows():
    codigo = limpiar_valor(row.get('CODIGO NUEVO', ''))
    if not codigo:
        codigo = limpiar_valor(row.get('CODIGO NUEVO ', ''))
    if not codigo:
        codigo = f'SIN-TES-{idx+1:04d}'
    tesis_excel_codigos.add(codigo)
    tesis_excel_titulos.add(limpiar_valor(row.get('TITULO', '')).strip().lower())

# Consultar en la base de datos
libros_db_codigos = set(Libro.objects.values_list('codigo_nuevo', flat=True))
libros_db_titulos = set(Libro.objects.values_list('titulo', flat=True))
tesis_db_codigos = set(TrabajoGrado.objects.values_list('codigo_nuevo', flat=True))
tesis_db_titulos = set(TrabajoGrado.objects.values_list('titulo', flat=True))

faltan_libros = libros_excel_codigos - libros_db_codigos
faltan_tesis = tesis_excel_codigos - tesis_db_codigos

print(f"Total libros en Excel: {len(libros_excel_codigos)}")
print(f"Total libros en BD: {len(libros_db_codigos)}")
print(f"Libros faltantes: {len(faltan_libros)}")
if faltan_libros:
    print('Códigos de libros faltantes:', list(faltan_libros)[:10])

print(f"Total tesis en Excel: {len(tesis_excel_codigos)}")
print(f"Total tesis en BD: {len(tesis_db_codigos)}")
print(f"Tesis faltantes: {len(faltan_tesis)}")
if faltan_tesis:
    print('Códigos de tesis faltantes:', list(faltan_tesis)[:10])
