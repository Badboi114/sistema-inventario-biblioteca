"""
Script para limpiar la base de datos y reimportar correctamente
Solo importa las hojas principales sin duplicados
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import transaction
from inventario.models import Libro, TrabajoGrado

print("\n" + "="*80)
print("LIMPIEZA DE BASE DE DATOS")
print("="*80)

# Contar registros actuales
total_libros = Libro.objects.count()
total_tesis = TrabajoGrado.objects.count()

print(f"Libros actuales: {total_libros}")
print(f"Tesis actuales: {total_tesis}")

confirmacion = input("\n¿Deseas eliminar TODOS los registros y comenzar de nuevo? (si/no): ")

if confirmacion.lower() == 'si':
    with transaction.atomic():
        Libro.objects.all().delete()
        TrabajoGrado.objects.all().delete()
    print("\n✅ Base de datos limpiada exitosamente")
    print(f"Libros restantes: {Libro.objects.count()}")
    print(f"Tesis restantes: {TrabajoGrado.objects.count()}")
else:
    print("\n❌ Operación cancelada")
