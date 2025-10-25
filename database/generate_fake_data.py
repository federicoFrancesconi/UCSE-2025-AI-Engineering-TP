#!/usr/bin/env python3
"""
Script para generar datos falsos realistas para la base de datos de streaming.
Utiliza la librería Faker para generar datos variados y realistas.

Requiere: pip install faker psycopg2-binary

Uso:
python generate_fake_data.py [--users N] [--content N] [--actors N] [--views N] [--ratings N]
"""

import argparse
import random
from datetime import timedelta, date
from faker import Faker
import psycopg2
from psycopg2.extras import execute_batch
import sys

# Configurar Faker con múltiples locales para más diversidad
fake = Faker(['es_ES', 'es_MX', 'es_AR', 'en_US', 'pt_BR'])

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'streaming',
    'user': 'federico',
    'password': 'password',  # Cambiar por tu contraseña
    'port': 5432
}

class StreamingDataGenerator:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        
        # Cache para IDs existentes
        self.plan_ids = []
        self.tipo_contenido_ids = []
        self.genero_ids = []
        self.clasificacion_ids = []
        
    def connect_db(self):
        """Conectar a la base de datos PostgreSQL"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            print("✓ Conexión a la base de datos establecida")
        except Exception as e:
            print(f"✗ Error conectando a la base de datos: {e}")
            sys.exit(1)
    
    def close_db(self):
        """Cerrar conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def load_reference_ids(self):
        """Cargar IDs de tablas de referencia"""
        try:
            # Cargar IDs de planes
            self.cursor.execute("SELECT id_plan FROM Planes")
            self.plan_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Cargar IDs de tipos de contenido
            self.cursor.execute("SELECT id_tipo_contenido FROM TipoContenido")
            self.tipo_contenido_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Cargar IDs de géneros
            self.cursor.execute("SELECT id_genero FROM Genero")
            self.genero_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Cargar IDs de clasificaciones
            self.cursor.execute("SELECT id_clasificacion FROM ClasificacionEdad")
            self.clasificacion_ids = [row[0] for row in self.cursor.fetchall()]
            
            print(f"✓ Referencias cargadas: {len(self.plan_ids)} planes, {len(self.genero_ids)} géneros")
            
        except Exception as e:
            print(f"✗ Error cargando referencias: {e}")
            sys.exit(1)
    
    def generate_users(self, count=1000):
        """Generar usuarios falsos"""
        print(f"Generando {count} usuarios...")
        
        users_data = []
        used_emails = set()
        
        paises = [
            'Argentina', 'Brasil', 'México', 'Colombia', 'Chile', 'Perú', 'Venezuela',
            'Ecuador', 'Uruguay', 'Paraguay', 'Bolivia', 'Costa Rica', 'Panamá',
            'Guatemala', 'Honduras', 'El Salvador', 'Nicaragua', 'República Dominicana',
            'Cuba', 'España', 'Estados Unidos', 'Canadá'
        ]
        
        generos = ['Masculino', 'Femenino', 'Otro', 'Prefiero no decir']
        
        for i in range(count):
            # Generar email único
            while True:
                email = fake.email()
                if email not in used_emails:
                    used_emails.add(email)
                    break
            
            # Fecha de registro entre enero 2022 y ahora
            fecha_registro = fake.date_between(start_date=date(2022, 1, 1), end_date=date.today())
            
            # Fecha de nacimiento entre 1950 y 2005
            fecha_nacimiento = fake.date_between(start_date=date(1950, 1, 1), end_date=date(2005, 12, 31))
            
            user_data = (
                fake.name(),
                email,
                fecha_registro,
                random.choice(paises),
                fecha_nacimiento,
                random.choice(generos)
            )
            users_data.append(user_data)
        
        # Insertar en lotes
        try:
            execute_batch(
                self.cursor,
                "INSERT INTO Usuarios (nombre, email, fecha_registro, pais, fecha_nacimiento, genero) VALUES (%s, %s, %s, %s, %s, %s)",
                users_data,
                page_size=100
            )
            self.conn.commit()
            print(f"✓ {count} usuarios insertados correctamente")
        except Exception as e:
            print(f"✗ Error insertando usuarios: {e}")
            self.conn.rollback()
    
    def generate_actors(self, count=500):
        """Generar actores falsos"""
        print(f"Generando {count} actores...")
        
        actors_data = []
        paises_actores = [
            'Estados Unidos', 'Reino Unido', 'España', 'Francia', 'Italia', 'Alemania',
            'Argentina', 'México', 'Brasil', 'Colombia', 'Australia', 'Canadá',
            'Japón', 'Corea del Sur', 'India', 'Suecia', 'Noruega', 'Dinamarca'
        ]
        
        for i in range(count):
            # Fecha de nacimiento entre 1930 y 2000 (para actores)
            fecha_nacimiento = fake.date_between(start_date=date(1930, 1, 1), end_date=date(2000, 12, 31))
            
            actor_data = (
                fake.name(),
                random.choice(paises_actores),
                fecha_nacimiento
            )
            actors_data.append(actor_data)
        
        try:
            execute_batch(
                self.cursor,
                "INSERT INTO Actores (nombre, pais, fecha_nacimiento) VALUES (%s, %s, %s)",
                actors_data,
                page_size=100
            )
            self.conn.commit()
            print(f"✓ {count} actores insertados correctamente")
        except Exception as e:
            print(f"✗ Error insertando actores: {e}")
            self.conn.rollback()
    
    def generate_content(self, count=1000):
        """Generar contenido falso"""
        print(f"Generando {count} contenidos...")
        
        content_data = []
        
        # Títulos base para diferentes géneros
        titulos_accion = [
            "Operación", "Misión", "El Último", "Código", "Venganza", "Rescate",
            "Infiltrado", "Cazador", "Soldado", "Comando", "Ataque", "Defensa"
        ]
        
        titulos_comedia = [
            "Risas en", "La Loca", "Aventuras de", "El Divertido", "Carcajadas",
            "Mi Vida Loca", "Familia", "Vecinos", "Oficina", "Escuela de"
        ]
        
        titulos_drama = [
            "El Corazón de", "Secretos de", "La Historia de", "Recuerdos",
            "El Destino de", "Lágrimas", "La Vida de", "Confesiones"
        ]
        
        titulos_scifi = [
            "Mundo", "Galaxia", "El Futuro", "Androides", "Viaje al",
            "Planeta", "Dimensión", "Tiempo", "Espacio", "Realidad"
        ]
        
        for i in range(count):
            genero_id = random.choice(self.genero_ids)
            
            # Generar título basado en el género
            if genero_id == 1:  # Acción
                titulo = f"{random.choice(titulos_accion)} {fake.word().capitalize()}"
            elif genero_id == 2:  # Comedia
                titulo = f"{random.choice(titulos_comedia)} {fake.word().capitalize()}"
            elif genero_id == 3:  # Drama
                titulo = f"{random.choice(titulos_drama)} {fake.word().capitalize()}"
            elif genero_id == 5:  # Ciencia Ficción
                titulo = f"{random.choice(titulos_scifi)} {fake.word().capitalize()}"
            else:
                titulo = f"{fake.word().capitalize()} {fake.word().capitalize()}"
            
            # Fecha de estreno entre 2020 y 2024
            fecha_estreno = fake.date_between(start_date=date(2020, 1, 1), end_date=date(2024, 12, 31))
            
            tipo_id = random.choice(self.tipo_contenido_ids)
            
            # Duración según tipo de contenido
            if tipo_id == 1:  # Película
                duracion = random.randint(80, 180)
            elif tipo_id == 2:  # Serie (episodio promedio)
                duracion = random.randint(25, 60)
            elif tipo_id == 3:  # Documental
                duracion = random.randint(45, 120)
            else:  # Especial
                duracion = random.randint(60, 150)
            
            content_data.append((
                titulo,
                tipo_id,
                genero_id,
                random.choice(self.clasificacion_ids),
                fecha_estreno,
                duracion
            ))
        
        try:
            execute_batch(
                self.cursor,
                "INSERT INTO Contenido (titulo, id_tipo_contenido, id_genero, id_clasificacion, fecha_estreno, duracion_min) VALUES (%s, %s, %s, %s, %s, %s)",
                content_data,
                page_size=100
            )
            self.conn.commit()
            print(f"✓ {count} contenidos insertados correctamente")
        except Exception as e:
            print(f"✗ Error insertando contenido: {e}")
            self.conn.rollback()
    
    def generate_subscriptions(self):
        """Generar suscripciones para todos los usuarios"""
        print("Generando suscripciones...")
        
        # Obtener IDs de usuarios
        self.cursor.execute("SELECT id_usuario, fecha_registro FROM Usuarios")
        usuarios = self.cursor.fetchall()
        
        subscriptions_data = []
        
        for user_id, fecha_registro in usuarios:
            # 90% de probabilidad de tener suscripción activa
            if random.random() < 0.9:
                plan_id = random.choice(self.plan_ids)
                
                # Obtener precio del plan
                self.cursor.execute("SELECT precio_mensual FROM Planes WHERE id_plan = %s", (plan_id,))
                precio = self.cursor.fetchone()[0]
                
                # Fecha de inicio entre fecha de registro y ahora
                fecha_inicio = fake.date_between(start_date=fecha_registro, end_date=date.today())
                
                # 80% suscripciones activas (sin fecha_fin)
                fecha_fin = None
                if random.random() < 0.2:
                    # Suscripción cancelada
                    fecha_fin = fake.date_between(start_date=fecha_inicio, end_date=date.today())
                
                subscriptions_data.append((
                    user_id,
                    plan_id,
                    fecha_inicio,
                    fecha_fin,
                    float(precio)
                ))
        
        try:
            execute_batch(
                self.cursor,
                "INSERT INTO Suscripciones (id_usuario, id_plan, fecha_inicio, fecha_fin, precio) VALUES (%s, %s, %s, %s, %s)",
                subscriptions_data,
                page_size=100
            )
            self.conn.commit()
            print(f"✓ {len(subscriptions_data)} suscripciones insertadas correctamente")
        except Exception as e:
            print(f"✗ Error insertando suscripciones: {e}")
            self.conn.rollback()
    
    def generate_views(self, count=10000):
        """Generar visualizaciones"""
        print(f"Generando {count} visualizaciones...")
        
        # Obtener IDs de usuarios y contenido
        self.cursor.execute("SELECT id_usuario FROM Usuarios")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        self.cursor.execute("SELECT id_contenido, duracion_min FROM Contenido")
        content_data = self.cursor.fetchall()
        
        views_data = []
        
        for i in range(count):
            user_id = random.choice(user_ids)
            content_id, duracion_total = random.choice(content_data)
            
            # Fecha de visualización en los últimos 12 meses
            fecha_view = fake.date_time_between(start_date='-12M', end_date='now')
            
            # Minutos vistos (entre 5 minutos y la duración completa)
            # Distribución realista: más probabilidad de ver completo o abandonar temprano
            rand_val = random.random()
            if rand_val < 0.3:  # 30% abandona temprano
                minutos_vistos = random.randint(5, min(30, duracion_total))
            elif rand_val < 0.6:  # 30% ve parcialmente
                min_parcial = min(30, int(duracion_total * 0.3))
                max_parcial = int(duracion_total * 0.8)
                if max_parcial > min_parcial:
                    minutos_vistos = random.randint(min_parcial, max_parcial)
                else:
                    minutos_vistos = random.randint(5, duracion_total)
            else:  # 40% ve completo
                minutos_vistos = duracion_total
            
            views_data.append((
                user_id,
                content_id,
                fecha_view,
                minutos_vistos
            ))
        
        try:
            execute_batch(
                self.cursor,
                "INSERT INTO Visualizaciones (id_usuario, id_contenido, fecha, minutos_vistos) VALUES (%s, %s, %s, %s)",
                views_data,
                page_size=100
            )
            self.conn.commit()
            print(f"✓ {count} visualizaciones insertadas correctamente")
        except Exception as e:
            print(f"✗ Error insertando visualizaciones: {e}")
            self.conn.rollback()
    
    def generate_ratings(self, count=5000):
        """Generar ratings"""
        print(f"Generando hasta {count} ratings...")
        
        # Obtener ratings existentes para evitar duplicados
        self.cursor.execute("SELECT id_usuario, id_contenido FROM Ratings")
        existing_ratings = set((row[0], row[1]) for row in self.cursor.fetchall())
        print(f"  Ratings existentes en la base de datos: {len(existing_ratings)}")
        
        # Obtener visualizaciones para generar ratings basados en ellas
        self.cursor.execute("""
            SELECT v.id_usuario, v.id_contenido, v.fecha, v.minutos_vistos, c.duracion_min
            FROM Visualizaciones v
            JOIN Contenido c ON v.id_contenido = c.id_contenido
            ORDER BY RANDOM()
            LIMIT %s
        """, (count * 3,))  # Obtener más visualizaciones para compensar duplicados
        
        visualizaciones = self.cursor.fetchall()
        ratings_data = []
        
        for user_id, content_id, fecha_view, minutos_vistos, duracion_total in visualizaciones:
            # Verificar que no exista ya este rating
            rating_key = (user_id, content_id)
            if rating_key in existing_ratings:
                continue
            
            # Solo 40% de las visualizaciones generan rating
            if random.random() < 0.4:
                # El rating depende de si vio el contenido completo
                porcentaje_visto = minutos_vistos / duracion_total
                
                if porcentaje_visto < 0.3:  # Vio menos del 30%
                    # Probabilidad alta de rating bajo
                    puntaje = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 20, 8, 2])[0]
                elif porcentaje_visto < 0.7:  # Vio 30-70%
                    # Rating medio
                    puntaje = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 40, 25, 5])[0]
                else:  # Vio más del 70%
                    # Probabilidad alta de rating alto
                    puntaje = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
                
                # Fecha de rating después de la visualización
                fecha_rating = fecha_view + timedelta(minutes=random.randint(1, 60))
                
                ratings_data.append((
                    user_id,
                    content_id,
                    puntaje,
                    fecha_rating
                ))
                
                # Marcar como usado para evitar duplicados en este lote
                existing_ratings.add(rating_key)
                
                # Detener si ya tenemos suficientes ratings
                if len(ratings_data) >= count:
                    break
        
        try:
            if ratings_data:
                execute_batch(
                    self.cursor,
                    "INSERT INTO Ratings (id_usuario, id_contenido, puntaje, fecha_rating) VALUES (%s, %s, %s, %s)",
                    ratings_data,
                    page_size=100
                )
                self.conn.commit()
                print(f"✓ {len(ratings_data)} ratings insertados correctamente")
            else:
                print("⚠ No hay nuevos ratings para insertar (todos los usuarios ya calificaron este contenido)")
        except Exception as e:
            print(f"✗ Error insertando ratings: {e}")
            self.conn.rollback()
    
    def generate_content_actor_relations(self):
        """Generar relaciones entre contenido y actores"""
        print("Generando relaciones contenido-actor...")
        
        # Obtener IDs
        self.cursor.execute("SELECT id_contenido FROM Contenido")
        content_ids = [row[0] for row in self.cursor.fetchall()]
        
        self.cursor.execute("SELECT id_actor FROM Actores")
        actor_ids = [row[0] for row in self.cursor.fetchall()]
        
        roles = [
            'Actor Principal', 'Actriz Principal', 'Actor de Reparto', 'Actriz de Reparto',
            'Director', 'Directora', 'Productor', 'Productora', 'Guionista',
            'Compositor', 'Narrador', 'Narradora'
        ]
        
        relations_data = []
        existing_relations = set()
        
        for content_id in content_ids:
            # Cada contenido tiene entre 2 y 8 personas involucradas
            num_relations = random.randint(2, 8)
            content_actors = random.sample(actor_ids, min(num_relations, len(actor_ids)))
            
            # Track roles used for this specific content to avoid duplicates
            used_roles_for_content = set()
            
            for i, actor_id in enumerate(content_actors):
                # Primer actor suele ser principal
                if i == 0:
                    rol = random.choice(['Actor Principal', 'Actriz Principal'])
                else:
                    rol = random.choice(roles)
                
                # Ensure unique combination of content_id, actor_id, and rol
                relation_key = (content_id, actor_id, rol)
                # If this exact combination exists, try a different role
                attempts = 0
                while relation_key in existing_relations and attempts < 10:
                    rol = random.choice(roles)
                    relation_key = (content_id, actor_id, rol)
                    attempts += 1
                
                if relation_key not in existing_relations:
                    existing_relations.add(relation_key)
                    relations_data.append(relation_key)
        
        try:
            execute_batch(
                self.cursor,
                "INSERT INTO Contenido_Actor (id_contenido, id_actor, rol) VALUES (%s, %s, %s)",
                relations_data,
                page_size=100
            )
            self.conn.commit()
            print(f"✓ {len(relations_data)} relaciones contenido-actor insertadas correctamente")
        except Exception as e:
            print(f"✗ Error insertando relaciones contenido-actor: {e}")
            self.conn.rollback()

def main():
    parser = argparse.ArgumentParser(description='Generar datos falsos para la base de datos de streaming')
    parser.add_argument('--users', type=int, default=1000, help='Número de usuarios a generar (default: 1000)')
    parser.add_argument('--content', type=int, default=1000, help='Número de contenidos a generar (default: 1000)')
    parser.add_argument('--actors', type=int, default=500, help='Número de actores a generar (default: 500)')
    parser.add_argument('--views', type=int, default=10000, help='Número de visualizaciones a generar (default: 10000)')
    parser.add_argument('--ratings', type=int, default=5000, help='Número máximo de ratings a generar (default: 5000)')
    
    args = parser.parse_args()
    
    generator = StreamingDataGenerator(DB_CONFIG)
    
    try:
        generator.connect_db()
        generator.load_reference_ids()
        
        print("🎬 Iniciando generación de datos para la plataforma de streaming...")
        print("=" * 60)
        
        # Generar datos en orden de dependencias
        generator.generate_users(args.users)
        generator.generate_actors(args.actors)
        generator.generate_content(args.content)
        generator.generate_subscriptions()  # Depende de usuarios
        generator.generate_content_actor_relations()  # Depende de contenido y actores
        generator.generate_views(args.views)  # Depende de usuarios y contenido
        generator.generate_ratings(args.ratings)  # Depende de visualizaciones
        
        print("=" * 60)
        print("✅ ¡Generación de datos completada exitosamente!")
        
        # Mostrar estadísticas
        generator.cursor.execute("SELECT COUNT(*) FROM Usuarios")
        users_count = generator.cursor.fetchone()[0]
        
        generator.cursor.execute("SELECT COUNT(*) FROM Contenido")
        content_count = generator.cursor.fetchone()[0]
        
        generator.cursor.execute("SELECT COUNT(*) FROM Visualizaciones")
        views_count = generator.cursor.fetchone()[0]
        
        generator.cursor.execute("SELECT COUNT(*) FROM Ratings")
        ratings_count = generator.cursor.fetchone()[0]
        
        print(f"""
📊 ESTADÍSTICAS FINALES:
   👥 Usuarios: {users_count:,}
   🎬 Contenidos: {content_count:,}
   👀 Visualizaciones: {views_count:,}
   ⭐ Ratings: {ratings_count:,}
""")
        
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        generator.close_db()

if __name__ == "__main__":
    main()
