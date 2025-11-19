import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import TrabajoGrado

# Total de tesis
total = TrabajoGrado.objects.count()
print(f'\n📊 Total de Tesis en Base de Datos: {total}')

# Distribución por prefijos
prefijos = {}
for t in TrabajoGrado.objects.exclude(codigo_nuevo__isnull=True).exclude(codigo_nuevo=''):
    prefijo = t.codigo_nuevo.split('-')[0] if '-' in t.codigo_nuevo else 'OTRO'
    prefijos[prefijo] = prefijos.get(prefijo, 0) + 1

print('\n📋 Distribución por Prefijo:')
for p, c in sorted(prefijos.items()):
    print(f'  {p}: {c} tesis')

# Verificar CPU-001 específicamente
cpu001 = TrabajoGrado.objects.filter(codigo_nuevo='CPU-001').first()
if cpu001:
    print(f'\n✅ CPU-001 ENCONTRADA:')
    print(f'   Título: {cpu001.titulo}')
    print(f'   Autor: {cpu001.autor}')
    print(f'   Carrera: {cpu001.carrera}')
else:
    print('\n❌ CPU-001 NO ENCONTRADA')

# Contar sin código
sin_codigo = TrabajoGrado.objects.filter(codigo_nuevo__isnull=True).count()
sin_codigo += TrabajoGrado.objects.filter(codigo_nuevo='').count()
print(f'\n⚠️ Tesis sin código: {sin_codigo}')
