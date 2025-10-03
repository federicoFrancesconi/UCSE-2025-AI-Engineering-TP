-- Script para crear las tablas del sistema de streaming
-- Base de datos: streaming

-- Usar la base de datos streaming
\c streaming;

-- ============================================
-- ELIMINAR TABLAS EXISTENTES (en orden inverso de dependencias)
-- ============================================

-- Eliminar tablas dependientes primero
DROP TABLE IF EXISTS Ratings CASCADE;
DROP TABLE IF EXISTS Visualizaciones CASCADE;
DROP TABLE IF EXISTS Contenido_Actor CASCADE;
DROP TABLE IF EXISTS Suscripciones CASCADE;

-- Eliminar tablas principales
DROP TABLE IF EXISTS Contenido CASCADE;
DROP TABLE IF EXISTS Actores CASCADE;
DROP TABLE IF EXISTS Usuarios CASCADE;

-- Eliminar tablas auxiliares
DROP TABLE IF EXISTS Planes CASCADE;
DROP TABLE IF EXISTS TipoContenido CASCADE;
DROP TABLE IF EXISTS Genero CASCADE;
DROP TABLE IF EXISTS ClasificacionEdad CASCADE;

-- ============================================
-- TABLAS AUXILIARES (catálogos de referencia)
-- ============================================

-- Tabla Planes
CREATE TABLE Planes (
    id_plan SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    precio_mensual DECIMAL(10,2) NOT NULL,
    calidad VARCHAR(20) NOT NULL,
    num_dispositivos INTEGER NOT NULL
);

-- Tabla TipoContenido
CREATE TABLE TipoContenido (
    id_tipo_contenido SERIAL PRIMARY KEY,
    descripcion VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla Genero
CREATE TABLE Genero (
    id_genero SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla ClasificacionEdad
CREATE TABLE ClasificacionEdad (
    id_clasificacion SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    descripcion VARCHAR(100) NOT NULL
);

-- ============================================
-- ENTIDADES PRINCIPALES
-- ============================================

-- Tabla Usuarios
CREATE TABLE Usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE,
    pais VARCHAR(50),
    fecha_nacimiento DATE,
    genero VARCHAR(20) CHECK (genero IN ('Masculino', 'Femenino', 'Otro', 'Prefiero no decir'))
);

-- Tabla Contenido
CREATE TABLE Contenido (
    id_contenido SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    id_tipo_contenido INTEGER NOT NULL,
    id_genero INTEGER NOT NULL,
    id_clasificacion INTEGER NOT NULL,
    fecha_estreno DATE,
    duracion_min INTEGER,
    FOREIGN KEY (id_tipo_contenido) REFERENCES TipoContenido(id_tipo_contenido),
    FOREIGN KEY (id_genero) REFERENCES Genero(id_genero),
    FOREIGN KEY (id_clasificacion) REFERENCES ClasificacionEdad(id_clasificacion)
);

-- Tabla Suscripciones
CREATE TABLE Suscripciones (
    id_suscripcion SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    id_plan INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_fin DATE,
    precio DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
    FOREIGN KEY (id_plan) REFERENCES Planes(id_plan)
);

-- Tabla Visualizaciones
CREATE TABLE Visualizaciones (
    id_visualizacion SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    id_contenido INTEGER NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    minutos_vistos INTEGER NOT NULL CHECK (minutos_vistos >= 0),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
    FOREIGN KEY (id_contenido) REFERENCES Contenido(id_contenido)
);

-- Tabla Ratings
CREATE TABLE Ratings (
    id_rating SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    id_contenido INTEGER NOT NULL,
    puntaje INTEGER NOT NULL CHECK (puntaje BETWEEN 1 AND 5),
    fecha_rating TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
    FOREIGN KEY (id_contenido) REFERENCES Contenido(id_contenido),
    UNIQUE(id_usuario, id_contenido) -- Un usuario solo puede calificar una vez cada contenido
);

-- Tabla Actores
CREATE TABLE Actores (
    id_actor SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    pais VARCHAR(50),
    fecha_nacimiento DATE
);

-- Tabla intermedia Contenido_Actor (relación N:M)
CREATE TABLE Contenido_Actor (
    id_contenido INTEGER NOT NULL,
    id_actor INTEGER NOT NULL,
    rol VARCHAR(50) NOT NULL, -- ej: "Actor Principal", "Director", "Productor"
    PRIMARY KEY (id_contenido, id_actor, rol),
    FOREIGN KEY (id_contenido) REFERENCES Contenido(id_contenido) ON DELETE CASCADE,
    FOREIGN KEY (id_actor) REFERENCES Actores(id_actor) ON DELETE CASCADE
);

-- ============================================
-- ÍNDICES PARA MEJORAR RENDIMIENTO
-- ============================================

-- Índices en campos que serán consultados frecuentemente
CREATE INDEX idx_visualizaciones_usuario ON Visualizaciones(id_usuario);
CREATE INDEX idx_visualizaciones_contenido ON Visualizaciones(id_contenido);
CREATE INDEX idx_visualizaciones_fecha ON Visualizaciones(fecha);
CREATE INDEX idx_ratings_usuario ON Ratings(id_usuario);
CREATE INDEX idx_ratings_contenido ON Ratings(id_contenido);
CREATE INDEX idx_contenido_genero ON Contenido(id_genero);
CREATE INDEX idx_contenido_tipo ON Contenido(id_tipo_contenido);
CREATE INDEX idx_suscripciones_usuario ON Suscripciones(id_usuario);
