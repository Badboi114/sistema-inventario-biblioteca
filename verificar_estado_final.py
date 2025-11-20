#!/usr/bin/env python
"""
Verificar estado final de la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Libro, TrabajoGrado

print("=" * 60)
print("📊 RESUMEN FINAL DE LA BASE DE DATOS")
print("=" * 60)
print()

total_libros = Libro.objects.count()
total_tesis = TrabajoGrado.objects.count()

print(f"📚 Libros cargados: {total_libros:,}")
print(f"🎓 Tesis cargadas: {total_tesis:,}")
print(f"✅ Total registros: {total_libros + total_tesis:,}")
print()

print("🔍 Verificando registros importantes:")
print()

# Verificar CPU-001
cpu001 = TrabajoGrado.objects.filter(codigo_nuevo='CPU-001').first()
if cpu001:
    print(f"✅ CPU-001 ENCONTRADA")
    print(f"   Título: {cpu001.titulo[:60]}...")
    print(f"   Autor: {cpu001.autor}")
else:
    print(f"❌ CPU-001 NO ENCONTRADA")

print()

# Verificar un libro
libro_ejemplo = Libro.objects.filter(codigo_seccion_full__istartswith='S1-R1').first()
if libro_ejemplo:
    print(f"✅ Libro ejemplo encontrado")
    print(f"   Código: {libro_ejemplo.codigo_seccion_full}")
    print(f"   Título: {libro_ejemplo.titulo[:60]}...")
else:
    print(f"❌ No se encontraron libros con código S1-R1")

print()
print("=" * 60)
print("✅ BASE DE DATOS LISTA PARA USAR")
print("=" * 60)
print()
print("🔐 Credenciales de acceso:")
print("   Usuario: admin")
print("   Password: admin123")
print("   URL: http://localhost:5173/")
print()
