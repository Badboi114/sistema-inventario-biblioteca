import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import TrabajoGrado

# Verificar CPU-007 específicamente
cpu007 = TrabajoGrado.objects.filter(codigo_nuevo='CPU-007').first()

if cpu007:
    print('\n✅ CPU-007 ENCONTRADA Y ACTUALIZADA:')
    print(f'   Código: {cpu007.codigo_nuevo}')
    print(f'   Título: {cpu007.titulo[:60]}...')
    print(f'   Autor: {cpu007.autor if cpu007.autor else "❌ VACÍO"}')
    print(f'   Tutor: {cpu007.tutor if cpu007.tutor else "❌ VACÍO"}')
    print(f'   Carrera: {cpu007.carrera if cpu007.carrera else "❌ VACÍO"}')
    print(f'   Año: {cpu007.anio if cpu007.anio else "❌ VACÍO"}')
    print(f'   Modalidad: {cpu007.modalidad if cpu007.modalidad else "❌ VACÍO"}')
    print(f'   Estado: {cpu007.estado}')
    
    # Verificar si tiene todos los datos
    if cpu007.autor and cpu007.tutor and cpu007.carrera and cpu007.anio:
        print('\n🎉 ¡TODOS LOS DATOS COMPLETOS!')
    else:
        print('\n⚠️ Aún faltan algunos datos')
else:
    print('\n❌ CPU-007 NO ENCONTRADA')

# Verificar algunas otras tesis CPU
print('\n📊 Muestra de otras tesis CPU:')
cpu_tesis = TrabajoGrado.objects.filter(codigo_nuevo__startswith='CPU-').order_by('codigo_nuevo')[:5]
for t in cpu_tesis:
    autor_status = '✅' if t.autor else '❌'
    tutor_status = '✅' if t.tutor else '❌'
    carrera_status = '✅' if t.carrera else '❌'
    print(f'  {t.codigo_nuevo}: Autor{autor_status} Tutor{tutor_status} Carrera{carrera_status}')
