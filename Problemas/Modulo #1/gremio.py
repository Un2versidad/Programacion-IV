import sqlite3
import os

def crear_base_datos():
    # Eliminar base de datos existente si existe
    if os.path.exists('aventuras.db'):
        os.remove('aventuras.db')

    # Conectar a la base de datos (la crea si no existe)
    conn = sqlite3.connect('aventuras.db')
    cursor = conn.cursor()

    # Crear tabla de héroes
    cursor.execute('''
    CREATE TABLE heroes (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        clase TEXT CHECK(clase IN ('Guerrero', 'Mago', 'Arquero', 'Clerigo', 'Ladron')),
        nivel_experiencia INTEGER CHECK(nivel_experiencia > 0)
    )
    ''')

    # Crear tabla de misiones
    cursor.execute('''
    CREATE TABLE misiones (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        nivel_dificultad INTEGER CHECK(nivel_dificultad BETWEEN 1 AND 10),
        localizacion TEXT NOT NULL,
        recompensa INTEGER CHECK(recompensa >= 0)
    )
    ''')

    # Crear tabla de monstruos
    cursor.execute('''
    CREATE TABLE monstruos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        nivel_amenaza INTEGER CHECK(nivel_amenaza BETWEEN 1 AND 10)
    )
    ''')

    # Crear tabla de unión misiones_heroes
    cursor.execute('''
    CREATE TABLE misiones_heroes (
        id INTEGER PRIMARY KEY,
        mision_id INTEGER,
        heroe_id INTEGER,
        FOREIGN KEY (mision_id) REFERENCES misiones (id),
        FOREIGN KEY (heroe_id) REFERENCES heroes (id),
        UNIQUE(mision_id, heroe_id)
    )
    ''')

    # Crear tabla de unión misiones_monstruos
    cursor.execute('''
    CREATE TABLE misiones_monstruos (
        id INTEGER PRIMARY KEY,
        mision_id INTEGER,
        monstruo_id INTEGER,
        FOREIGN KEY (mision_id) REFERENCES misiones (id),
        FOREIGN KEY (monstruo_id) REFERENCES monstruos (id),
        UNIQUE(mision_id, monstruo_id)
    )
    ''')

    # Insertar datos de prueba
    insertar_datos_ficticios(cursor)

    # Confirmar cambios y cerrar conexión
    conn.commit()
    conn.close()

    print("¡Base de datos creada correctamente!")

def insertar_datos_ficticios(cursor):
    # Insertar héroes
    heroes = [
        (1, 'Aragorn', 'Guerrero', 8),
        (2, 'Gandalf', 'Mago', 10),
        (3, 'Legolas', 'Arquero', 7),
        (4, 'Frodo', 'Ladron', 4),
        (5, 'Galadriel', 'Mago', 9)
    ]
    cursor.executemany("INSERT INTO heroes VALUES (?, ?, ?, ?)", heroes)

    # Insertar misiones
    misiones = [
        (1, 'Rescate en la Montaña', 5, 'Montañas Nubladas', 500),
        (2, 'Tesoro Perdido', 3, 'Bosque Encantado', 300),
        (3, 'Batalla Final', 10, 'Mordor', 1000),
        (4, 'Escolta de Mercaderes', 2, 'Camino Real', 200)
    ]
    cursor.executemany("INSERT INTO misiones VALUES (?, ?, ?, ?, ?)", misiones)

    # Insertar monstruos
    monstruos = [
        (1, 'Smaug', 'Dragón', 10),
        (2, 'Orco Capitán', 'Orco', 5),
        (3, 'Rey Brujo', 'No-muerto', 8),
        (4, 'Trasgo', 'Goblin', 2),
        (5, 'Araña Gigante', 'Bestia', 6)
    ]
    cursor.executemany("INSERT INTO monstruos VALUES (?, ?, ?, ?)", monstruos)

    # Insertar relaciones misión-héroe
    misiones_heroes = [
        (1, 1, 1),  # Aragorn en Rescate
        (2, 1, 3),  # Legolas en Rescate
        (3, 2, 4),  # Frodo en Tesoro Perdido
        (4, 3, 1),  # Aragorn en Batalla Final
        (5, 3, 2),  # Gandalf en Batalla Final
        (6, 3, 3),  # Legolas en Batalla Final
        (7, 4, 4),  # Frodo en Escolta
        (8, 4, 5)   # Galadriel en Escolta
    ]
    cursor.executemany("INSERT INTO misiones_heroes VALUES (?, ?, ?)", misiones_heroes)

    # Insertar relaciones misión-monstruo
    misiones_monstruos = [
        (1, 1, 2),  # Orco Capitán en Rescate
        (2, 1, 4),  # Trasgo en Rescate
        (3, 2, 5),  # Araña Gigante en Tesoro Perdido
        (4, 3, 1),  # Smaug en Batalla Final
        (5, 3, 3),  # Rey Brujo en Batalla Final
        (6, 4, 4)   # Trasgo en Escolta
    ]
    cursor.executemany("INSERT INTO misiones_monstruos VALUES (?, ?, ?)", misiones_monstruos)

def main():
    crear_base_datos()

if __name__ == "__main__":
    main()