# Scripts de Datos para Sistema de Streaming

Este directorio contiene los scripts necesarios para crear y poblar la base de datos del sistema de streaming con datos de prueba.

## Archivos

- `create_streaming_tables.sql` - Script para crear todas las tablas del sistema
- `insert_sample_data.sql` - Script con datos de ejemplo básicos (20 usuarios, 30 contenidos)
- `generate_fake_data.py` - Script Python para generar grandes volúmenes de datos falsos realistas
- `requirements.txt` - Dependencias Python necesarias

## Instalación y Configuración

### 1. Crear la Base de Datos

Primero, crea la base de datos en PostgreSQL:

```bash
# Conectar como superusuario
psql -U postgres

# Crear base de datos
CREATE DATABASE streaming;
\q
```

### 2. Crear las Tablas

Ejecuta el script de creación de tablas:

```bash
psql -U postgres -d streaming -f create_streaming_tables.sql
```

### 3. Insertar Datos Básicos

Para datos de ejemplo básicos (recomendado para desarrollo inicial):

```bash
psql -U postgres -d streaming -f insert_sample_data.sql
```

### 4. Generar Datos Masivos (Opcional)

Para generar grandes volúmenes de datos de prueba:

#### Instalar dependencias Python:

```bash
pip install -r requirements.txt
```

#### Configurar la conexión a la base de datos:

Edita el archivo `generate_fake_data.py` y modifica la configuración de `DB_CONFIG`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'streaming',
    'user': 'tu_usuario',
    'password': 'tu_contraseña',
    'port': 5432
}
```

#### Ejecutar el generador:

```bash
# Usar valores por defecto (1000 usuarios, 1000 contenidos, etc.)
python generate_fake_data.py

# Personalizar cantidades
python generate_fake_data.py --users 5000 --content 2000 --actors 1000 --views 50000 --ratings 25000

# Ver todas las opciones
python generate_fake_data.py --help
```

## Estructura de Datos Generados

### Datos Básicos (insert_sample_data.sql)
- **20 usuarios** de diferentes países latinoamericanos
- **20 actores** internacionales conocidos
- **29 contenidos** variados (películas, series, documentales, especiales)
- **Suscripciones** para todos los usuarios
- **75+ visualizaciones** realistas
- **40+ ratings** coherentes con las visualizaciones
- **Relaciones contenido-actor** apropiadas

### Datos Masivos (generate_fake_data.py)
- **Usuarios**: Nombres, emails, países, fechas de nacimiento variados
- **Actores**: De múltiples países con fechas de nacimiento realistas
- **Contenido**: Títulos generados según género, duraciones apropiadas por tipo
- **Suscripciones**: 90% de usuarios con suscripción activa
- **Visualizaciones**: Patrones realistas (algunos completos, otros abandonados)
- **Ratings**: Correlacionados con el porcentaje visto del contenido

## Características de los Datos Generados

### Realismo
- **Emails únicos** para todos los usuarios
- **Fechas coherentes** (registro antes de visualización, rating después de ver)
- **Distribución realista** de ratings basada en tiempo visto
- **Países y nombres** apropiados para cada región
- **Duraciones** apropiadas según tipo de contenido

### Relaciones
- Los ratings se generan solo para contenido visualizado
- Las fechas de rating son posteriores a las visualizaciones
- Los usuarios solo pueden calificar una vez cada contenido
- Las suscripciones inician después del registro del usuario

### Variedad
- **22 países** diferentes para usuarios
- **18 países** diferentes para actores
- **Múltiples géneros** y tipos de contenido
- **Roles variados** para actores (principal, reparto, director, etc.)

## Consultas de Ejemplo

Una vez poblada la base de datos, puedes probar estas consultas:

```sql
-- Usuarios más activos
SELECT u.nombre, COUNT(v.id_visualizacion) as visualizaciones
FROM Usuarios u
JOIN Visualizaciones v ON u.id_usuario = v.id_usuario
GROUP BY u.id_usuario, u.nombre
ORDER BY visualizaciones DESC
LIMIT 10;

-- Contenido mejor calificado
SELECT c.titulo, AVG(r.puntaje) as promedio_rating, COUNT(r.id_rating) as num_ratings
FROM Contenido c
JOIN Ratings r ON c.id_contenido = r.id_contenido
GROUP BY c.id_contenido, c.titulo
HAVING COUNT(r.id_rating) >= 5
ORDER BY promedio_rating DESC
LIMIT 10;

-- Estadísticas por género
SELECT g.nombre, COUNT(c.id_contenido) as num_contenidos, AVG(c.duracion_min) as duracion_promedio
FROM Genero g
JOIN Contenido c ON g.id_genero = c.id_genero
GROUP BY g.id_genero, g.nombre
ORDER BY num_contenidos DESC;
```

## Solución de Problemas

### Error de conexión a PostgreSQL
- Verifica que PostgreSQL esté ejecutándose
- Confirma las credenciales en `DB_CONFIG`
- Asegúrate de que el usuario tenga permisos en la base de datos

### Error de memoria con datos masivos
- Reduce el tamaño de los lotes en `execute_batch`
- Genera los datos en múltiples ejecuciones con menos registros
