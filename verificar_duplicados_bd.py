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

# Verificar duplicados por código
libros_codigos = list(Libro.objects.values_list('codigo_nuevo', flat=True))
duplicados_libros = [item for item, count in Counter(libros_codigos).items() if count > 1]

# Verificar duplicados por título
libros_titulos = list(Libro.objects.values_list('titulo', flat=True))
duplicados_titulos = [item for item, count in Counter(libros_titulos).items() if count > 1]

tesis_codigos = list(TrabajoGrado.objects.values_list('codigo_nuevo', flat=True))
duplicados_tesis = [item for item, count in Counter(tesis_codigos).items() if count > 1]

tesis_titulos = list(TrabajoGrado.objects.values_list('titulo', flat=True))
duplicados_titulos_tesis = [item for item, count in Counter(tesis_titulos).items() if count > 1]

print(f"Duplicados en códigos de libros: {len(duplicados_libros)}")
if duplicados_libros:
    print('Ejemplo:', duplicados_libros[:10])
print(f"Duplicados en títulos de libros: {len(duplicados_titulos)}")
if duplicados_titulos:
    print('Ejemplo:', duplicados_titulos[:10])
print(f"Duplicados en códigos de tesis: {len(duplicados_tesis)}")
if duplicados_tesis:
    print('Ejemplo:', duplicados_tesis[:10])
print(f"Duplicados en títulos de tesis: {len(duplicados_titulos_tesis)}")
if duplicados_titulos_tesis:
    print('Ejemplo:', duplicados_titulos_tesis[:10])
