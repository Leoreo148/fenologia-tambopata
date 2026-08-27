-- =====================================================================
-- ESQUEMA OFICIAL SUPABASE: THE MACAW SOCIETY · FENOLOGÍA TAMBOPATA
-- =====================================================================

-- 1. LIMPIEZA DE TABLAS ANTIGUAS (SI EXISTEN)
DROP TABLE IF EXISTS evaluaciones_fenologicas CASCADE;
DROP TABLE IF EXISTS arboles CASCADE;
DROP TABLE IF EXISTS parcelas CASCADE;
DROP TABLE IF EXISTS pronostico_clima CASCADE;

-- 2. TABLA: PARCELAS (25 Parcelas georreferenciadas con hábitat y altitud)
CREATE TABLE parcelas (
    codigo VARCHAR(10) PRIMARY KEY, -- ej: TF1, AG1, FP1, BS1
    habitat VARCHAR(50) NOT NULL,    -- Bosque de Tierra Firme, Aguajal, Bajío, Sucesional
    este_utm REAL NOT NULL,
    norte_utm REAL NOT NULL,
    altura_msnm REAL NOT NULL,
    latitud REAL NOT NULL,
    longitud REAL NOT NULL,
    prefijo_nomenclatura VARCHAR(5) NOT NULL, -- BTF, BAG, BB, BS
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. TABLA: ARBOLES (Censo Maestro de 1,939 árboles individuales con placa TAG)
CREATE TABLE arboles (
    id BIGSERIAL PRIMARY KEY,
    plop VARCHAR(10) REFERENCES parcelas(codigo) ON DELETE CASCADE,
    sub VARCHAR(10) NOT NULL,        -- Subparcela: 1a, 1b, 2a, etc.
    tag INTEGER,                     -- Placa metálica: 1001, 1002, 3421, etc.
    nombre_cientifico VARCHAR(150) NOT NULL,
    genero VARCHAR(50) NOT NULL,
    estado_vital VARCHAR(30) DEFAULT 'Normal',
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. TABLA: EVALUACIONES_FENOLOGICAS (Registros mensuales de campo)
CREATE TABLE evaluaciones_fenologicas (
    id VARCHAR(100) PRIMARY KEY,     -- UUID o Código compuesto ej: TF1_1001_2026-08-27
    tag INTEGER,
    plop VARCHAR(10) REFERENCES parcelas(codigo) ON DELETE CASCADE,
    sub VARCHAR(10) NOT NULL,
    nombre_cientifico VARCHAR(150),
    fecha DATE NOT NULL,
    mes INTEGER NOT NULL,
    anio INTEGER NOT NULL,
    boton INTEGER DEFAULT 0 CHECK (boton >= 0 AND boton <= 4),
    flor INTEGER DEFAULT 0 CHECK (flor >= 0 AND flor <= 4),
    fruto_verde INTEGER DEFAULT 0 CHECK (fruto_verde >= 0 AND fruto_verde <= 4),
    fruto_maduro INTEGER DEFAULT 0 CHECK (fruto_maduro >= 0 AND fruto_maduro <= 4),
    diseminado INTEGER DEFAULT 0 CHECK (diseminado >= 0 AND diseminado <= 4),
    estado_vital VARCHAR(30) DEFAULT 'Normal',
    notas TEXT,
    foto_url TEXT,
    evaluador VARCHAR(100) DEFAULT 'Investigador',
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. HABILITAR PERMISOS COMPLETOS (ROW LEVEL SECURITY PARA LA APP MÓVIL)
ALTER TABLE parcelas ENABLE ROW LEVEL SECURITY;
ALTER TABLE arboles ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluaciones_fenologicas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Acceso total parcelas" ON parcelas FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Acceso total arboles" ON arboles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Acceso total evaluaciones" ON evaluaciones_fenologicas FOR ALL USING (true) WITH CHECK (true);
