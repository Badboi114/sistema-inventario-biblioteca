import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import TrabajoGrado

total = TrabajoGrado.objects.count()
print(f'\n📖 TOTAL TESIS CARGADAS: {total}')

# Verificar CPU-001
cpu001 = TrabajoGrado.objects.filter(codigo_nuevo='CPU-001').first()
if cpu001:
    print(f'✅ CPU-001 ENCONTRADA')
    print(f'   Título: {cpu001.titulo[:60]}...')
    print(f'   Autor: {cpu001.autor}')
else:
    print(f'❌ CPU-001 NO ESTÁ EN ESTA HOJA')
    print(f'   (Esta tesis podría estar en la otra hoja)')

# Ver distribución de prefijos
print(f'\n📊 Distribución por Prefijo:')
prefijos = {}
for t in TrabajoGrado.objects.exclude(codigo_nuevo__isnull=True).exclude(codigo_nuevo=''):
    prefijo = t.codigo_nuevo.split('-')[0] if '-' in t.codigo_nuevo else 'OTRO'
    prefijos[prefijo] = prefijos.get(prefijo, 0) + 1

for p, c in sorted(prefijos.items())[:15]:
    print(f'  {p}: {c}')

# Contar tesis CPU
cpu_count = TrabajoGrado.objects.filter(codigo_nuevo__startswith='CPU-').count()
print(f'\n🔢 Total tesis CPU: {cpu_count}')
