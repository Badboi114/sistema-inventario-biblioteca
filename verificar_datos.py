import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Libro, TrabajoGrado

libros = Libro.objects.count()
tesis = TrabajoGrado.objects.count()
total = libros + tesis

print(f"\n{'='*50}")
print(f"  📚 RESUMEN DE LA BASE DE DATOS")
print(f"{'='*50}")
print(f"  Libros académicos:     {libros:,}")
print(f"  Trabajos de grado:     {tesis:,}")
print(f"  {'-'*48}")
print(f"  TOTAL:                 {total:,}")
print(f"{'='*50}\n")

# Mostrar algunos ejemplos
print("Ejemplos de Libros:")
for libro in Libro.objects.all()[:3]:
    print(f"  • {libro.codigo_nuevo}: {libro.titulo[:60]}")

print("\nEjemplos de Trabajos de Grado:")
for trabajo in TrabajoGrado.objects.all()[:3]:
    print(f"  • {trabajo.codigo_nuevo}: {trabajo.titulo[:60]}")
