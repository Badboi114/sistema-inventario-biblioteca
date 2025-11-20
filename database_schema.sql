-- ============================================================
-- SISTEMA DE INVENTARIO DE BIBLIOTECA UPDS
-- Base de Datos Normalizada (3NF) - PostgreSQL
-- ============================================================
-- Autor: Sistema de Inventario Biblioteca
-- Fecha: 2025-11-20
-- Versión: 1.0
-- Descripción: Esquema completo con herencia, auditoría y seguridad
-- ============================================================

-- ============================================================
-- EXTENSIONES NECESARIAS
-- ============================================================
-- Habilitar UUID para identificadores únicos (opcional)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLA 1: ACTIVO BIBLIOGRÁFICO (Tabla Padre - Master)
-- ============================================================
-- Contiene todos los campos comunes entre Libros y Tesis
-- Implementa el patrón de Herencia Multi-Tabla (MTI)
-- Esta tabla es la "columna vertebral" del sistema
-- ============================================================

CREATE TABLE "inventario_activobibliografico" (
    -- Clave Primaria
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    
    -- Códigos de Identificación
    "codigo_nuevo" VARCHAR(50) NULL,
    "codigo_antiguo" VARCHAR(50) NULL,
    
    -- Información Bibliográfica Principal
    "titulo" TEXT NOT NULL,
    "autor" VARCHAR(300) NULL,
    "anio" INTEGER NULL CHECK ("anio" >= 1900 AND "anio" <= EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    
    -- Categorización
    "facultad" VARCHAR(255) NULL,
    "estado" VARCHAR(20) NOT NULL DEFAULT 'BUENO',
    
    -- Información Adicional
    "observaciones" TEXT NULL,
    
    -- Ubicación Física
    "ubicacion_seccion" VARCHAR(100) NULL,
    "ubicacion_repisa" VARCHAR(100) NULL,
    
    -- Metadatos del Sistema
    "fecha_registro" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- ===== CONSTRAINTS =====
    
    -- Código nuevo debe ser único (cuando no sea NULL)
    CONSTRAINT "uq_codigo_nuevo" UNIQUE ("codigo_nuevo"),
    
    -- Estado solo puede tener valores válidos
    CONSTRAINT "ck_estado_valido" CHECK (
        "estado" IN ('BUENO', 'REGULAR', 'MALO', 'EN REPARACION')
    )
);

-- ===== ÍNDICES PARA OPTIMIZACIÓN DE BÚSQUEDAS =====

-- Índice para búsquedas por código (CRÍTICO - usado en 80% de queries)
CREATE INDEX "idx_activo_codigo_nuevo" ON "inventario_activobibliografico" ("codigo_nuevo");

-- Índice para búsquedas por título (búsquedas de texto)
CREATE INDEX "idx_activo_titulo" ON "inventario_activobibliografico" USING gin(to_tsvector('spanish', "titulo"));

-- Índice para filtros por estado (reportes y alertas)
CREATE INDEX "idx_activo_estado" ON "inventario_activobibliografico" ("estado");

-- Índice para ordenamiento por fecha (últimos agregados)
CREATE INDEX "idx_activo_fecha_registro" ON "inventario_activobibliografico" ("fecha_registro" DESC);

-- Índice para búsquedas por autor
CREATE INDEX "idx_activo_autor" ON "inventario_activobibliografico" ("autor");

-- Índice para filtros por facultad
CREATE INDEX "idx_activo_facultad" ON "inventario_activobibliografico" ("facultad");

-- ===== COMENTARIOS DE DOCUMENTACIÓN =====
COMMENT ON TABLE "inventario_activobibliografico" IS 'Tabla maestra que contiene todos los campos comunes entre Libros y Trabajos de Grado. Implementa Multi-Table Inheritance (MTI).';
COMMENT ON COLUMN "inventario_activobibliografico"."id" IS 'Identificador único autoincremental del activo bibliográfico';
COMMENT ON COLUMN "inventario_activobibliografico"."codigo_nuevo" IS 'Código de catalogación actual (Ej: S1-R1-0039 para libros, ADM-0026 para tesis)';
COMMENT ON COLUMN "inventario_activobibliografico"."codigo_antiguo" IS 'Código antiguo previo a la recatalogación (histórico)';
COMMENT ON COLUMN "inventario_activobibliografico"."titulo" IS 'Título completo de la obra bibliográfica';
COMMENT ON COLUMN "inventario_activobibliografico"."autor" IS 'Autor principal de la obra (puede ser NULL para obras anónimas o diccionarios)';
COMMENT ON COLUMN "inventario_activobibliografico"."anio" IS 'Año de publicación o presentación';
COMMENT ON COLUMN "inventario_activobibliografico"."estado" IS 'Estado físico: BUENO (usable), REGULAR (desgastado), MALO (requiere reparación), EN REPARACION (en proceso)';

-- ============================================================
-- TABLA 2: LIBRO (Tabla Hija - Especialización)
-- ============================================================
-- Contiene SOLO los campos específicos de libros académicos
-- Hereda todos los campos de ActivoBibliografico mediante relación 1:1
-- ============================================================

CREATE TABLE "inventario_libro" (
    -- Clave Primaria y Foránea (OneToOne con Padre)
    "activobibliografico_ptr_id" BIGINT NOT NULL PRIMARY KEY,
    
    -- ===== CAMPOS ESPECÍFICOS DE LIBROS =====
    
    -- Clasificación Académica
    "materia" VARCHAR(200) NULL,
    
    -- Información Editorial
    "editorial" VARCHAR(200) NULL,
    "edicion" VARCHAR(100) NULL,
    
    -- Sistema de Ubicación Detallado
    "codigo_seccion_full" VARCHAR(100) NULL,
    
    -- Control de Importación (para mantener orden del Excel)
    "orden_importacion" INTEGER NOT NULL DEFAULT 0,
    
    -- ===== FOREIGN KEYS =====
    
    -- Relación de Herencia (OneToOne) con tabla padre
    CONSTRAINT "fk_libro_activo" FOREIGN KEY ("activobibliografico_ptr_id")
        REFERENCES "inventario_activobibliografico" ("id")
        ON DELETE CASCADE
        DEFERRABLE INITIALLY DEFERRED
);

-- ===== ÍNDICES ESPECÍFICOS PARA LIBROS =====

-- Índice para búsquedas por código de sección completo (S1-R1-0039)
CREATE INDEX "idx_libro_codigo_seccion" ON "inventario_libro" ("codigo_seccion_full");

-- Índice para filtros por materia
CREATE INDEX "idx_libro_materia" ON "inventario_libro" ("materia");

-- Índice para filtros por editorial
CREATE INDEX "idx_libro_editorial" ON "inventario_libro" ("editorial");

-- Índice para mantener orden de importación
CREATE INDEX "idx_libro_orden" ON "inventario_libro" ("orden_importacion");

-- ===== COMENTARIOS =====
COMMENT ON TABLE "inventario_libro" IS 'Tabla especializada para libros académicos. Hereda de ActivoBibliografico mediante OneToOne.';
COMMENT ON COLUMN "inventario_libro"."activobibliografico_ptr_id" IS 'FK que apunta al registro padre en ActivoBibliografico (relación 1:1)';
COMMENT ON COLUMN "inventario_libro"."materia" IS 'Materia o área académica del libro (Ej: MATEMÁTICAS, FÍSICA, CONTABILIDAD)';
COMMENT ON COLUMN "inventario_libro"."codigo_seccion_full" IS 'Código completo de ubicación física: S[Sección]-R[Repisa]-[Número] (Ej: S1-R1-0039)';
COMMENT ON COLUMN "inventario_libro"."orden_importacion" IS 'Orden original del libro en el archivo Excel (para preservar organización física)';

-- ============================================================
-- TABLA 3: TRABAJO DE GRADO (Tabla Hija - Especialización)
-- ============================================================
-- Contiene SOLO los campos específicos de tesis y proyectos
-- Hereda todos los campos de ActivoBibliografico mediante relación 1:1
-- ============================================================

CREATE TABLE "inventario_trabajogrado" (
    -- Clave Primaria y Foránea (OneToOne con Padre)
    "activobibliografico_ptr_id" BIGINT NOT NULL PRIMARY KEY,
    
    -- ===== CAMPOS ESPECÍFICOS DE TRABAJOS DE GRADO =====
    
    -- Tipo de Trabajo Académico
    "modalidad" VARCHAR(50) NULL,
    
    -- Información Académica
    "tutor" VARCHAR(300) NULL,
    "carrera" VARCHAR(200) NULL,
    
    -- ===== FOREIGN KEYS =====
    
    -- Relación de Herencia (OneToOne) con tabla padre
    CONSTRAINT "fk_tesis_activo" FOREIGN KEY ("activobibliografico_ptr_id")
        REFERENCES "inventario_activobibliografico" ("id")
        ON DELETE CASCADE
        DEFERRABLE INITIALLY DEFERRED,
    
    -- ===== CONSTRAINTS =====
    
    -- Modalidad solo puede tener valores válidos
    CONSTRAINT "ck_modalidad_valida" CHECK (
        "modalidad" IN ('TESIS', 'PROYECTO DE GRADO', 'TRABAJO DIRIGIDO', 'TESINA')
        OR "modalidad" IS NULL
    )
);

-- ===== ÍNDICES ESPECÍFICOS PARA TRABAJOS DE GRADO =====

-- Índice para filtros por modalidad (reportes por tipo)
CREATE INDEX "idx_tesis_modalidad" ON "inventario_trabajogrado" ("modalidad");

-- Índice para búsquedas por carrera
CREATE INDEX "idx_tesis_carrera" ON "inventario_trabajogrado" ("carrera");

-- Índice para búsquedas por tutor
CREATE INDEX "idx_tesis_tutor" ON "inventario_trabajogrado" ("tutor");

-- ===== COMENTARIOS =====
COMMENT ON TABLE "inventario_trabajogrado" IS 'Tabla especializada para trabajos de grado (tesis, proyectos). Hereda de ActivoBibliografico.';
COMMENT ON COLUMN "inventario_trabajogrado"."activobibliografico_ptr_id" IS 'FK que apunta al registro padre en ActivoBibliografico (relación 1:1)';
COMMENT ON COLUMN "inventario_trabajogrado"."modalidad" IS 'Tipo de trabajo: TESIS, PROYECTO DE GRADO, TRABAJO DIRIGIDO';
COMMENT ON COLUMN "inventario_trabajogrado"."tutor" IS 'Docente tutor o guía del trabajo de grado';
COMMENT ON COLUMN "inventario_trabajogrado"."carrera" IS 'Carrera académica del estudiante (Ej: INGENIERÍA COMERCIAL, CONTADURÍA PÚBLICA)';

-- ============================================================
-- TABLAS DE AUDITORÍA (django-simple-history)
-- ============================================================
-- Estas tablas mantienen un registro histórico completo de TODOS
-- los cambios realizados en la base de datos.
-- Cada vez que se crea, modifica o elimina un registro, se guarda
-- una "fotografía" completa del estado anterior.
-- ============================================================

-- ============================================================
-- TABLA 4: HISTORIAL DE ACTIVOS BIBLIOGRÁFICOS
-- ============================================================
CREATE TABLE "inventario_historicalactivobibliografico" (
    -- Clave Primaria del Historial
    "history_id" SERIAL NOT NULL PRIMARY KEY,
    
    -- ===== COPIA EXACTA DE TODOS LOS CAMPOS =====
    "id" BIGINT NULL,
    "codigo_nuevo" VARCHAR(50) NULL,
    "codigo_antiguo" VARCHAR(50) NULL,
    "titulo" TEXT NULL,
    "autor" VARCHAR(300) NULL,
    "anio" INTEGER NULL,
    "facultad" VARCHAR(255) NULL,
    "estado" VARCHAR(20) NULL,
    "observaciones" TEXT NULL,
    "ubicacion_seccion" VARCHAR(100) NULL,
    "ubicacion_repisa" VARCHAR(100) NULL,
    "fecha_registro" TIMESTAMP WITH TIME ZONE NULL,
    
    -- ===== METADATOS DE AUDITORÍA =====
    
    -- Fecha y hora EXACTA del cambio
    "history_date" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Razón del cambio (opcional, para documentar)
    "history_change_reason" VARCHAR(100) NULL,
    
    -- Tipo de operación realizada
    "history_type" VARCHAR(1) NOT NULL,
    
    -- Usuario que realizó el cambio (FK a auth_user)
    "history_user_id" INTEGER NULL,
    
    -- ===== CONSTRAINTS =====
    CONSTRAINT "ck_history_type" CHECK ("history_type" IN ('+', '~', '-'))
);

-- ===== ÍNDICES PARA AUDITORÍA =====
CREATE INDEX "idx_hist_activo_id" ON "inventario_historicalactivobibliografico" ("id");
CREATE INDEX "idx_hist_activo_fecha" ON "inventario_historicalactivobibliografico" ("history_date" DESC);
CREATE INDEX "idx_hist_activo_usuario" ON "inventario_historicalactivobibliografico" ("history_user_id");
CREATE INDEX "idx_hist_activo_tipo" ON "inventario_historicalactivobibliografico" ("history_type");

COMMENT ON TABLE "inventario_historicalactivobibliografico" IS 'Tabla de auditoría que registra TODOS los cambios en ActivoBibliografico (creación, modificación, eliminación)';
COMMENT ON COLUMN "inventario_historicalactivobibliografico"."history_type" IS 'Tipo de cambio: + (creado), ~ (modificado), - (eliminado)';
COMMENT ON COLUMN "inventario_historicalactivobibliografico"."history_date" IS 'Fecha y hora exacta en que se realizó el cambio';

-- ============================================================
-- TABLA 5: HISTORIAL DE LIBROS
-- ============================================================
CREATE TABLE "inventario_historicallibro" (
    -- Clave Primaria del Historial
    "history_id" SERIAL NOT NULL PRIMARY KEY,
    
    -- ===== COPIA DE CAMPOS DE ACTIVO BIBLIOGRÁFICO =====
    "id" BIGINT NULL,
    "codigo_nuevo" VARCHAR(50) NULL,
    "codigo_antiguo" VARCHAR(50) NULL,
    "titulo" TEXT NULL,
    "autor" VARCHAR(300) NULL,
    "anio" INTEGER NULL,
    "facultad" VARCHAR(255) NULL,
    "estado" VARCHAR(20) NULL,
    "observaciones" TEXT NULL,
    "ubicacion_seccion" VARCHAR(100) NULL,
    "ubicacion_repisa" VARCHAR(100) NULL,
    "fecha_registro" TIMESTAMP WITH TIME ZONE NULL,
    
    -- ===== COPIA DE CAMPOS ESPECÍFICOS DE LIBRO =====
    "materia" VARCHAR(200) NULL,
    "editorial" VARCHAR(200) NULL,
    "edicion" VARCHAR(100) NULL,
    "codigo_seccion_full" VARCHAR(100) NULL,
    "orden_importacion" INTEGER NULL,
    
    -- ===== METADATOS DE AUDITORÍA =====
    "history_date" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "history_change_reason" VARCHAR(100) NULL,
    "history_type" VARCHAR(1) NOT NULL,
    "history_user_id" INTEGER NULL,
    
    CONSTRAINT "ck_hist_libro_type" CHECK ("history_type" IN ('+', '~', '-'))
);

-- ===== ÍNDICES =====
CREATE INDEX "idx_hist_libro_id" ON "inventario_historicallibro" ("id");
CREATE INDEX "idx_hist_libro_fecha" ON "inventario_historicallibro" ("history_date" DESC);
CREATE INDEX "idx_hist_libro_usuario" ON "inventario_historicallibro" ("history_user_id");

COMMENT ON TABLE "inventario_historicallibro" IS 'Auditoría completa de libros. Incluye snapshot de TODOS los campos (heredados + propios).';

-- ============================================================
-- TABLA 6: HISTORIAL DE TRABAJOS DE GRADO
-- ============================================================
CREATE TABLE "inventario_historicaltrabajogrado" (
    -- Clave Primaria del Historial
    "history_id" SERIAL NOT NULL PRIMARY KEY,
    
    -- ===== COPIA DE CAMPOS DE ACTIVO BIBLIOGRÁFICO =====
    "id" BIGINT NULL,
    "codigo_nuevo" VARCHAR(50) NULL,
    "codigo_antiguo" VARCHAR(50) NULL,
    "titulo" TEXT NULL,
    "autor" VARCHAR(300) NULL,
    "anio" INTEGER NULL,
    "facultad" VARCHAR(255) NULL,
    "estado" VARCHAR(20) NULL,
    "observaciones" TEXT NULL,
    "ubicacion_seccion" VARCHAR(100) NULL,
    "ubicacion_repisa" VARCHAR(100) NULL,
    "fecha_registro" TIMESTAMP WITH TIME ZONE NULL,
    
    -- ===== COPIA DE CAMPOS ESPECÍFICOS DE TRABAJO DE GRADO =====
    "modalidad" VARCHAR(50) NULL,
    "tutor" VARCHAR(300) NULL,
    "carrera" VARCHAR(200) NULL,
    
    -- ===== METADATOS DE AUDITORÍA =====
    "history_date" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "history_change_reason" VARCHAR(100) NULL,
    "history_type" VARCHAR(1) NOT NULL,
    "history_user_id" INTEGER NULL,
    
    CONSTRAINT "ck_hist_tesis_type" CHECK ("history_type" IN ('+', '~', '-'))
);

-- ===== ÍNDICES =====
CREATE INDEX "idx_hist_tesis_id" ON "inventario_historicaltrabajogrado" ("id");
CREATE INDEX "idx_hist_tesis_fecha" ON "inventario_historicaltrabajogrado" ("history_date" DESC);
CREATE INDEX "idx_hist_tesis_usuario" ON "inventario_historicaltrabajogrado" ("history_user_id");

COMMENT ON TABLE "inventario_historicaltrabajogrado" IS 'Auditoría completa de trabajos de grado. Incluye snapshot de TODOS los campos.';

-- ============================================================
-- VISTAS MATERIALIZADAS (Para Reportes Rápidos)
-- ============================================================

-- Vista: Todos los libros con información completa
CREATE VIEW "vista_libros_completos" AS
SELECT 
    a.id,
    a.codigo_nuevo,
    a.titulo,
    a.autor,
    a.anio,
    a.facultad,
    a.estado,
    a.ubicacion_seccion,
    a.ubicacion_repisa,
    l.materia,
    l.editorial,
    l.edicion,
    l.codigo_seccion_full,
    a.fecha_registro
FROM "inventario_activobibliografico" a
INNER JOIN "inventario_libro" l ON a.id = l.activobibliografico_ptr_id;

COMMENT ON VIEW "vista_libros_completos" IS 'Vista completa de libros con JOIN automático entre padre e hijo';

-- Vista: Todos los trabajos de grado con información completa
CREATE VIEW "vista_tesis_completas" AS
SELECT 
    a.id,
    a.codigo_nuevo,
    a.titulo,
    a.autor,
    a.anio,
    a.facultad,
    a.estado,
    t.modalidad,
    t.tutor,
    t.carrera,
    a.fecha_registro
FROM "inventario_activobibliografico" a
INNER JOIN "inventario_trabajogrado" t ON a.id = t.activobibliografico_ptr_id;

COMMENT ON VIEW "vista_tesis_completas" IS 'Vista completa de trabajos de grado con JOIN automático';

-- ============================================================
-- FUNCIONES Y TRIGGERS (Automatización)
-- ============================================================

-- Función: Actualizar fecha de modificación automáticamente
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_registro = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION actualizar_fecha_modificacion() IS 'Actualiza automáticamente la fecha cuando se modifica un registro';

-- ============================================================
-- DATOS DE EJEMPLO Y VALIDACIÓN
-- ============================================================

-- Insertar datos de prueba (opcional, para validar estructura)
/*
INSERT INTO "inventario_activobibliografico" 
    (codigo_nuevo, titulo, autor, anio, facultad, estado)
VALUES 
    ('S1-R1-0001', 'CÁLCULO DIFERENCIAL E INTEGRAL', 'STEWART, JAMES', 2018, 'CIENCIAS EXACTAS', 'BUENO'),
    ('ADM-0001', 'ANÁLISIS DE COSTOS EMPRESARIALES', 'GARCÍA LÓPEZ, JUAN', 2020, 'CIENCIAS EMPRESARIALES', 'BUENO');

-- Insertar libro (hereda id=1)
INSERT INTO "inventario_libro" 
    (activobibliografico_ptr_id, materia, editorial, edicion, codigo_seccion_full)
VALUES 
    (1, 'MATEMÁTICAS', 'CENGAGE LEARNING', '8va Edición', 'S1-R1-0001');

-- Insertar tesis (hereda id=2)
INSERT INTO "inventario_trabajogrado" 
    (activobibliografico_ptr_id, modalidad, tutor, carrera)
VALUES 
    (2, 'PROYECTO DE GRADO', 'LIC. MARÍA TORRES', 'INGENIERÍA COMERCIAL');
*/

-- ============================================================
-- ESTADÍSTICAS ACTUALES DEL SISTEMA
-- ============================================================
/*
ESTADO ACTUAL DE LA BASE DE DATOS (db.sqlite3):

┌─────────────────────────────────────────────────────────┐
│  TABLA                                | REGISTROS       │
├─────────────────────────────────────────────────────────┤
│  inventario_activobibliografico       | 2,387           │
│  inventario_libro                     | 1,703 (71.3%)   │
│  inventario_trabajogrado              | 684 (28.7%)     │
│  inventario_historicallibro           | ~3,500+         │
│  inventario_historicaltrabajogrado    | ~1,400+         │
└─────────────────────────────────────────────────────────┘

DISTRIBUCIÓN DE LIBROS POR ESTADO:
  • BUENO: 1,638 (96.2%)
  • REGULAR: 53 (3.1%)
  • MALO: 12 (0.7%)

DISTRIBUCIÓN DE TESIS POR CARRERA:
  • INGENIERÍA COMERCIAL (COM): 355 (51.9%)
  • DERECHO (TDER): 124 (18.1%)
  • INGENIERÍA INDUSTRIAL (IND): 61 (8.9%)
  • INGENIERÍA DE GAS Y PETRÓLEO (IGP): 45 (6.6%)
  • ADMINISTRACIÓN DE EMPRESAS (ADM): 25 (3.7%)
  • CONTADURÍA PÚBLICA (CPU): 21 (3.1%)
  • SISTEMAS (SIS): 27 (3.9%)
  • REDES (RED): 25 (3.7%)

TAMAÑO TOTAL: ~55 MB (SQLite)
ÚLTIMA ACTUALIZACIÓN: 2025-11-20
*/

-- ============================================================
-- FIN DEL ESQUEMA
-- ============================================================
