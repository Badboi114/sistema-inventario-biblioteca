import os
import django
from django.db.models import Q

# Configuración Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Libro

def auditar_libros():
    total = Libro.objects.count()
    print(f"\n📊 AUDITORÍA DE CALIDAD DE LIBROS ({total} total)\n")
    print("=" * 60)

    # 1. Buscar libros "Zombie" (Sin título o título vacío)
    zombies = Libro.objects.filter(Q(titulo__isnull=True) | Q(titulo=''))
    print(f"\n❌ Libros sin Título: {zombies.count()}")
    if zombies.count() > 0:
        print("   ⚠️ CRÍTICO: Todos los libros deberían tener título")
        for z in zombies[:5]:
            print(f"      ID {z.id}: {z.codigo_nuevo or 'S/C'}")

    # 2. Buscar libros "Huérfanos" (Sin Autor)
    huerfanos = Libro.objects.filter(Q(autor__isnull=True) | Q(autor=''))
    print(f"\n⚠️ Libros sin Autor: {huerfanos.count()}")
    print("   (Nota: Algunos libros como diccionarios pueden no tener autor, es normal)")
    if huerfanos.count() > 0 and huerfanos.count() < 20:
        print("   Ejemplos:")
        for h in huerfanos[:5]:
            print(f"      [{h.codigo_nuevo or 'S/C'}] {h.titulo[:50]}...")

    # 3. Buscar libros "Incompletos" (Sin Editorial Y sin Año)
    incompletos = Libro.objects.filter(
        (Q(editorial__isnull=True) | Q(editorial='')) & 
        (Q(anio__isnull=True))
    )
    print(f"\n⚠️ Libros sin Editorial NI Año: {incompletos.count()}")
    if incompletos.count() > 0 and incompletos.count() < 20:
        print("   Ejemplos:")
        for inc in incompletos[:5]:
            print(f"      [{inc.codigo_nuevo or 'S/C'}] {inc.titulo[:50]}...")

    # 4. Verificar códigos de sección (S1-R1-XXXX)
    sin_codigo_seccion = Libro.objects.filter(Q(codigo_seccion_full__isnull=True) | Q(codigo_seccion_full=''))
    print(f"\n📍 Libros sin Código de Sección (S1-R1-XXX): {sin_codigo_seccion.count()}")

    # 5. Verificar código nuevo
    sin_codigo_nuevo = Libro.objects.filter(Q(codigo_nuevo__isnull=True) | Q(codigo_nuevo=''))
    print(f"\n🏷️ Libros sin Código Nuevo: {sin_codigo_nuevo.count()}")

    # 6. Muestreo aleatorio para revisión humana
    print("\n" + "=" * 60)
    print("🔍 MUESTREO ALEATORIO (10 Libros):")
    print("=" * 60)
    import random
    ids = list(Libro.objects.values_list('id', flat=True))
    if ids:
        random_ids = random.sample(ids, min(len(ids), 10))
        muestra = Libro.objects.filter(id__in=random_ids).order_by('id')
        for i, m in enumerate(muestra, 1):
            titulo = m.titulo[:40] + "..." if len(m.titulo) > 40 else m.titulo
            autor = m.autor[:25] + "..." if m.autor and len(m.autor) > 25 else (m.autor or "N/A")
            editorial = m.editorial[:20] + "..." if m.editorial and len(m.editorial) > 20 else (m.editorial or "N/A")
            codigo_seccion = m.codigo_seccion_full or "N/A"
            
            print(f"\n{i}. Código: {m.codigo_nuevo or 'S/C'}")
            print(f"   Título: {titulo}")
            print(f"   Autor: {autor}")
            print(f"   Editorial: {editorial} | Año: {m.anio or 'N/A'}")
            print(f"   Ubicación: {codigo_seccion}")
            print(f"   Estado: {m.estado}")

    # 7. Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE AUDITORÍA:")
    print("=" * 60)
    print(f"✅ Total de Libros: {total}")
    
    if zombies.count() == 0:
        print("✅ Títulos: Todos los libros tienen título")
    else:
        print(f"❌ Títulos: {zombies.count()} libros sin título (CRÍTICO)")
    
    porcentaje_sin_autor = (huerfanos.count() / total * 100) if total > 0 else 0
    if porcentaje_sin_autor < 5:
        print(f"✅ Autores: {huerfanos.count()} sin autor ({porcentaje_sin_autor:.1f}% - Normal)")
    else:
        print(f"⚠️ Autores: {huerfanos.count()} sin autor ({porcentaje_sin_autor:.1f}% - Revisar)")
    
    porcentaje_incompletos = (incompletos.count() / total * 100) if total > 0 else 0
    if porcentaje_incompletos < 10:
        print(f"✅ Metadatos: {incompletos.count()} sin editorial ni año ({porcentaje_incompletos:.1f}% - Aceptable)")
    else:
        print(f"⚠️ Metadatos: {incompletos.count()} sin editorial ni año ({porcentaje_incompletos:.1f}% - Revisar)")
    
    print("\n" + "=" * 60)
    print("🎯 VEREDICTO:")
    if zombies.count() == 0 and porcentaje_sin_autor < 10 and porcentaje_incompletos < 15:
        print("✅ Los libros están EN BUEN ESTADO. No se detectaron problemas críticos.")
    else:
        print("⚠️ Se detectaron algunas inconsistencias. Revisar arriba.")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    auditar_libros()
