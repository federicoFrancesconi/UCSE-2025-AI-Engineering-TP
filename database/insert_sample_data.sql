-- Script para insertar datos de ejemplo en las tablas del sistema de streaming

-- Usar la base de datos streaming
\c streaming;

BEGIN;

-- ============================================
-- LIMPIAR TABLAS (en orden de dependencias)
-- ============================================

-- Limpiar tablas dependientes primero
TRUNCATE TABLE Ratings CASCADE;
TRUNCATE TABLE Visualizaciones CASCADE;
TRUNCATE TABLE Contenido_Actor CASCADE;
TRUNCATE TABLE Suscripciones CASCADE;

-- Limpiar tablas principales
TRUNCATE TABLE Contenido CASCADE;
TRUNCATE TABLE Actores CASCADE;
TRUNCATE TABLE Usuarios CASCADE;

-- Limpiar tablas auxiliares (referencias)
TRUNCATE TABLE Planes CASCADE;
TRUNCATE TABLE TipoContenido CASCADE;
TRUNCATE TABLE Genero CASCADE;
TRUNCATE TABLE ClasificacionEdad CASCADE;

-- ============================================
-- DATOS PARA TABLAS AUXILIARES (Referencias)
-- ============================================

-- Insertar planes
INSERT INTO Planes (nombre, precio_mensual, calidad, num_dispositivos) VALUES
('Básico', 9.99, 'SD', 1),
('Estándar', 15.99, 'HD', 2),
('Premium', 19.99, '4K', 4);

-- Insertar tipos de contenido
INSERT INTO TipoContenido (descripcion) VALUES
('Película'),
('Serie'),
('Documental'),
('Especial');

-- Insertar géneros
INSERT INTO Genero (nombre) VALUES
('Acción'),
('Comedia'),
('Drama'),
('Terror'),
('Ciencia Ficción'),
('Romance'),
('Thriller'),
('Animación'),
('Aventura'),
('Misterio');

-- Insertar clasificaciones de edad
INSERT INTO ClasificacionEdad (codigo, descripcion) VALUES
('G', 'Apto para toda la familia'),
('PG', 'Se sugiere supervisión de los padres'),
('PG-13', 'Mayores de 13 años'),
('R', 'Restringido - Menores de 17 requieren acompañante adulto'),
('+13', 'Mayores de 13 años'),
('+16', 'Mayores de 16 años'),
('+18', 'Solo para adultos');

-- ============================================
-- DATOS PARA USUARIOS
-- ============================================

INSERT INTO Usuarios (nombre, email, fecha_registro, pais, fecha_nacimiento, genero) VALUES
('Juan Pérez', 'juan.perez@email.com', '2023-01-15', 'Argentina', '1990-05-12', 'Masculino'),
('María García', 'maria.garcia@email.com', '2023-02-20', 'España', '1985-08-25', 'Femenino'),
('Carlos Rodriguez', 'carlos.rodriguez@email.com', '2023-03-10', 'México', '1992-11-03', 'Masculino'),
('Ana Martínez', 'ana.martinez@email.com', '2023-01-28', 'Colombia', '1988-02-14', 'Femenino'),
('Luis Fernández', 'luis.fernandez@email.com', '2023-04-05', 'Chile', '1995-07-20', 'Masculino'),
('Sofia López', 'sofia.lopez@email.com', '2023-02-12', 'Perú', '1993-12-08', 'Femenino'),
('Diego Sánchez', 'diego.sanchez@email.com', '2023-03-25', 'Uruguay', '1987-04-17', 'Masculino'),
('Valentina Torres', 'valentina.torres@email.com', '2023-01-08', 'Ecuador', '1991-09-30', 'Femenino'),
('Andrés Morales', 'andres.morales@email.com', '2023-05-14', 'Bolivia', '1989-01-22', 'Masculino'),
('Camila Herrera', 'camila.herrera@email.com', '2023-02-28', 'Paraguay', '1994-06-15', 'Femenino'),
('Roberto Silva', 'roberto.silva@email.com', '2023-04-18', 'Brasil', '1986-10-05', 'Masculino'),
('Isabella Cruz', 'isabella.cruz@email.com', '2023-03-15', 'Venezuela', '1990-03-28', 'Femenino'),
('Alejandro Ruiz', 'alejandro.ruiz@email.com', '2023-01-30', 'Costa Rica', '1992-08-11', 'Masculino'),
('Natalia Vargas', 'natalia.vargas@email.com', '2023-05-02', 'Panamá', '1988-12-03', 'Femenino'),
('Fernando Castro', 'fernando.castro@email.com', '2023-02-08', 'Guatemala', '1995-04-25', 'Masculino'),
('Daniela Reyes', 'daniela.reyes@email.com', '2023-04-22', 'Honduras', '1993-07-18', 'Femenino'),
('Gabriel Mendoza', 'gabriel.mendoza@email.com', '2023-03-12', 'El Salvador', '1987-11-12', 'Masculino'),
('Lucía Jiménez', 'lucia.jimenez@email.com', '2023-01-18', 'Nicaragua', '1991-05-07', 'Femenino'),
('Sebastián Flores', 'sebastian.flores@email.com', '2023-05-08', 'República Dominicana', '1989-09-14', 'Masculino'),
('Valeria Campos', 'valeria.campos@email.com', '2023-02-25', 'Cuba', '1994-01-29', 'Femenino');

-- ============================================
-- DATOS PARA ACTORES
-- ============================================

INSERT INTO Actores (nombre, pais, fecha_nacimiento) VALUES
('Leonardo DiCaprio', 'Estados Unidos', '1974-11-11'),
('Meryl Streep', 'Estados Unidos', '1949-06-22'),
('Robert De Niro', 'Estados Unidos', '1943-08-17'),
('Scarlett Johansson', 'Estados Unidos', '1984-11-22'),
('Brad Pitt', 'Estados Unidos', '1963-12-18'),
('Cate Blanchett', 'Australia', '1969-05-14'),
('Javier Bardem', 'España', '1969-03-01'),
('Penélope Cruz', 'España', '1974-04-28'),
('Antonio Banderas', 'España', '1960-08-10'),
('Gael García Bernal', 'México', '1978-11-30'),
('Diego Luna', 'México', '1979-12-29'),
('Wagner Moura', 'Brasil', '1976-06-27'),
('Ricardo Darín', 'Argentina', '1957-01-16'),
('Natalie Portman', 'Israel', '1981-06-09'),
('Marion Cotillard', 'Francia', '1975-09-30'),
('Jean Reno', 'Marruecos', '1948-07-30'),
('Tilda Swinton', 'Reino Unido', '1960-11-05'),
('Hugh Jackman', 'Australia', '1968-10-12'),
('Russell Crowe', 'Nueva Zelanda', '1964-04-07'),
('Nicole Kidman', 'Australia', '1967-06-20');

-- ============================================
-- DATOS PARA CONTENIDO
-- ============================================

INSERT INTO Contenido (titulo, id_tipo_contenido, id_genero, id_clasificacion, fecha_estreno, duracion_min) VALUES
-- Películas
('El Origen de los Sueños', 1, 5, 3, '1995-03-15', 148),
('Corazones Perdidos', 1, 6, 2, '1998-05-20', 125),
('La Última Frontera', 1, 1, 4, '2001-07-08', 156),
('Risas en el Café', 1, 2, 1, '2004-02-14', 98),
('El Misterio del Faro', 1, 10, 3, '2007-09-12', 134),
('Aventuras en el Amazonas', 1, 9, 2, '2010-04-25', 142),
('Terror Nocturno', 1, 4, 5, '2013-10-31', 105),
('La Casa del Tiempo', 1, 5, 3, '2016-06-18', 128),
('Amor en Primavera', 1, 6, 1, '2019-03-22', 112),
('Persecución Extrema', 1, 7, 4, '2022-08-15', 118),

-- Series
('Detectives del Futuro', 2, 7, 3, '1996-01-10', 45),
('Familias Modernas', 2, 2, 2, '1999-02-05', 30),
('El Imperio del Crimen', 2, 3, 5, '2002-03-20', 55),
('Historias de Miedo', 2, 4, 4, '2005-10-01', 40),
('Aventuras Galácticas', 2, 5, 2, '2008-04-12', 50),
('Secretos del Corazón', 2, 6, 3, '2011-05-08', 42),
('La Academia de Espías', 2, 1, 3, '2014-06-25', 48),
('Mundos Paralelos', 2, 5, 4, '2017-07-30', 52),
('Comedia Central', 2, 2, 2, '2020-01-25', 25),
('El Último Detective', 2, 10, 4, '2023-09-05', 47),

-- Documentales
('Vida Salvaje de África', 3, 3, 1, '1997-04-20', 85),
('Historia de la Humanidad', 3, 3, 2, '2000-06-10', 120),
('Océanos Profundos', 3, 3, 1, '2003-08-22', 95),
('Tecnología del Futuro', 3, 5, 2, '2006-05-15', 75),
('Arte y Cultura', 3, 3, 1, '2009-07-12', 110),

-- Especiales
('Concierto de Estrellas', 4, 2, 1, '2012-12-31', 90),
('Stand-up de Medianoche', 4, 2, 3, '2015-11-15', 65),
('Festival de Animación', 4, 8, 1, '2018-08-05', 125),
('Especial de Navidad', 4, 2, 1, '2021-12-25', 80),
('Gala de Premios', 4, 2, 2, '2024-11-20', 150);

-- ============================================
-- DATOS PARA CONTENIDO_ACTOR
-- ============================================

INSERT INTO Contenido_Actor (id_contenido, id_actor, rol) VALUES
-- El Origen de los Sueños
(1, 1, 'Actor Principal'),
(1, 4, 'Actriz Principal'),
(1, 2, 'Director'),

-- Corazones Perdidos
(2, 6, 'Actriz Principal'),
(2, 5, 'Actor Principal'),
(2, 15, 'Director'),

-- La Última Frontera
(3, 3, 'Actor Principal'),
(3, 17, 'Actriz de Reparto'),
(3, 18, 'Director'),

-- Risas en el Café
(4, 7, 'Actor Principal'),
(4, 8, 'Actriz Principal'),

-- El Misterio del Faro
(5, 19, 'Actor Principal'),
(5, 20, 'Actriz Principal'),

-- Series
(11, 4, 'Actriz Principal'),
(11, 1, 'Productor Ejecutivo'),
(12, 8, 'Actriz Principal'),
(12, 10, 'Actor Principal'),
(13, 12, 'Actor Principal'),
(13, 7, 'Actor de Reparto'),

-- Documentales
(21, 2, 'Narrador'),
(22, 16, 'Narrador'),
(23, 20, 'Narradora');

-- ============================================
-- DATOS PARA SUSCRIPCIONES
-- ============================================

INSERT INTO Suscripciones (id_usuario, id_plan, fecha_inicio, fecha_fin, precio) VALUES
(1, 2, '2023-01-15', '2024-01-15', 15.99),
(2, 3, '2023-02-20', '2024-02-20', 19.99),
(3, 1, '2023-03-10', '2024-03-10', 9.99),
(4, 2, '2023-01-28', '2024-01-28', 15.99),
(5, 3, '2023-04-05', '2024-04-05', 19.99),
(6, 1, '2023-02-12', '2024-02-12', 9.99),
(7, 2, '2023-03-25', '2024-03-25', 15.99),
(8, 3, '2023-01-08', '2024-01-08', 19.99),
(9, 1, '2023-05-14', '2024-05-14', 9.99),
(10, 2, '2023-02-28', '2024-02-28', 15.99),
(11, 3, '2023-04-18', '2024-04-18', 19.99),
(12, 1, '2023-03-15', '2024-03-15', 9.99),
(13, 2, '2023-01-30', '2024-01-30', 15.99),
(14, 3, '2023-05-02', '2024-05-02', 19.99),
(15, 1, '2023-02-08', '2024-02-08', 9.99),
(16, 2, '2023-04-22', '2024-04-22', 15.99),
(17, 3, '2023-03-12', '2024-03-12', 19.99),
(18, 1, '2023-01-18', '2024-01-18', 9.99),
(19, 2, '2023-05-08', '2024-05-08', 15.99),
(20, 3, '2023-02-25', '2024-02-25', 19.99);

-- ============================================
-- DATOS PARA VISUALIZACIONES
-- ============================================

INSERT INTO Visualizaciones (id_usuario, id_contenido, fecha, minutos_vistos) VALUES
-- Usuario 1
(1, 1, '2023-03-16 20:30:00', 148), -- Vio completa
(1, 2, '2023-05-21 19:15:00', 87),  -- Vio parcial
(1, 11, '2023-01-15 21:00:00', 45), -- Vio episodio completo
(1, 12, '2023-02-10 20:45:00', 30), -- Vio episodio completo
(1, 21, '2023-04-22 15:30:00', 85), -- Vio documental completo

-- Usuario 2
(2, 3, '2023-07-10 22:00:00', 156), -- Vio completa
(2, 4, '2023-02-20 18:30:00', 98),  -- Vio completa
(2, 13, '2023-03-25 21:30:00', 55), -- Vio episodio completo
(2, 14, '2023-10-05 20:00:00', 25), -- Vio parcial

-- Usuario 3
(3, 5, '2023-09-15 19:45:00', 134), -- Vio completa
(3, 6, '2023-04-28 20:15:00', 100), -- Vio parcial
(3, 15, '2023-04-15 21:45:00', 50), -- Vio episodio completo
(3, 16, '2023-05-12 19:30:00', 42), -- Vio episodio completo

-- Usuario 4
(4, 7, '2023-11-02 22:30:00', 105), -- Vio completa
(4, 8, '2023-06-20 20:00:00', 128), -- Vio completa
(4, 17, '2023-06-28 21:15:00', 48), -- Vio episodio completo

-- Usuario 5
(5, 9, '2023-03-25 19:00:00', 112), -- Vio completa
(5, 10, '2023-08-18 20:45:00', 90), -- Vio parcial
(5, 18, '2023-08-02 21:30:00', 52), -- Vio episodio completo
(5, 22, '2023-06-15 16:00:00', 120), -- Vio documental completo

-- Más visualizaciones para otros usuarios
(6, 1, '2023-03-20 21:00:00', 120),
(6, 11, '2023-01-20 20:30:00', 45),
(7, 2, '2023-05-25 19:45:00', 125),
(7, 12, '2023-02-15 21:15:00', 30),
(8, 3, '2023-07-15 22:15:00', 140),
(8, 13, '2023-03-30 20:45:00', 55),
(9, 4, '2023-02-25 18:45:00', 98),
(9, 14, '2023-10-10 19:30:00', 35),
(10, 5, '2023-09-20 21:00:00', 134),
(10, 15, '2023-04-20 20:15:00', 50),
(11, 6, '2023-05-02 19:30:00', 142),
(11, 16, '2023-05-15 21:45:00', 42),
(12, 7, '2023-11-05 22:45:00', 80),
(12, 17, '2023-07-02 20:30:00', 48),
(13, 8, '2023-06-25 19:15:00', 128),
(13, 18, '2023-08-05 21:00:00', 52),
(14, 9, '2023-03-28 20:00:00', 112),
(14, 19, '2023-01-30 21:30:00', 25),
(15, 10, '2023-08-20 21:15:00', 118),
(15, 20, '2023-09-08 20:45:00', 47);

-- ============================================
-- DATOS PARA RATINGS
-- ============================================

INSERT INTO Ratings (id_usuario, id_contenido, puntaje, fecha_rating) VALUES
-- Ratings para películas (fixed invalid time formats)
(1, 1, 5, '2023-03-16 22:58:00'), -- Después de ver
(1, 2, 3, '2023-05-21 21:15:00'),
(2, 3, 5, '2023-07-11 00:36:00'),
(2, 4, 4, '2023-02-20 20:08:00'),
(3, 5, 4, '2023-09-15 21:59:00'),
(3, 6, 2, '2023-04-28 22:00:00'), -- No le gustó porque no la terminó
(4, 7, 5, '2023-11-03 00:15:00'),
(4, 8, 4, '2023-06-20 22:08:00'),
(5, 9, 5, '2023-03-25 20:52:00'),
(5, 10, 3, '2023-08-18 22:20:00'), -- Rating medio porque no la terminó

-- Ratings para series
(1, 11, 4, '2023-01-15 21:45:00'),
(1, 12, 5, '2023-02-10 21:15:00'),
(2, 13, 4, '2023-03-25 22:25:00'),
(2, 14, 2, '2023-10-05 20:30:00'), -- No le gustó
(3, 15, 5, '2023-04-15 22:35:00'),
(3, 16, 4, '2023-05-12 20:12:00'),
(4, 17, 5, '2023-06-28 22:03:00'),
(5, 18, 4, '2023-08-02 22:22:00'),

-- Ratings para documentales
(1, 21, 5, '2023-04-22 16:55:00'),
(5, 22, 4, '2023-06-15 18:00:00'),

-- Más ratings de otros usuarios
(6, 1, 4, '2023-03-20 23:00:00'),
(7, 2, 5, '2023-05-25 21:50:00'),
(8, 3, 5, '2023-07-16 00:15:00'),
(9, 4, 4, '2023-02-25 20:23:00'),
(10, 5, 5, '2023-09-20 23:14:00'),
(11, 6, 4, '2023-05-02 21:52:00'),
(12, 7, 3, '2023-11-05 23:30:00'),
(13, 8, 5, '2023-06-25 21:23:00'),
(14, 9, 4, '2023-03-28 22:12:00'),
(15, 10, 4, '2023-08-20 23:33:00');

COMMIT;
