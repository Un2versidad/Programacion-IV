import sqlite3
from datetime import datetime

def conectar():
    return sqlite3.connect("fauna_en_peligro.db")

def crear_tablas():
    con = conectar()
    cur = con.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS animales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_comun TEXT NOT NULL,
        nombre_cientifico TEXT NOT NULL,
        nivel_peligro TEXT CHECK(nivel_peligro IN ('Vulnerable', 'En Peligro', 'Críticamente Amenazado'))
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS habitats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS animales_habitats (
        animal_id INTEGER,
        habitat_id INTEGER,
        PRIMARY KEY(animal_id, habitat_id),
        FOREIGN KEY(animal_id) REFERENCES animales(id),
        FOREIGN KEY(habitat_id) REFERENCES habitats(id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS observaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_id INTEGER,
        fecha TEXT,
        lugar TEXT,
        observador TEXT,
        FOREIGN KEY(animal_id) REFERENCES animales(id)
    )
    ''')

    con.commit()
    con.close()

# CRUD animales
def agregar_animal(nombre_comun, nombre_cientifico, nivel_peligro):
    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT INTO animales(nombre_comun, nombre_cientifico, nivel_peligro) VALUES (?, ?, ?)",
                (nombre_comun, nombre_cientifico, nivel_peligro))
    con.commit()
    con.close()

def listar_animales():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM animales")
    return cur.fetchall()

# CRUD hábitats
def agregar_habitat(nombre, descripcion):
    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT INTO habitats(nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
    con.commit()
    con.close()

def listar_habitats():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM habitats")
    return cur.fetchall()

def asignar_habitat_a_animal(animal_id, habitat_id):
    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO animales_habitats(animal_id, habitat_id) VALUES (?, ?)",
                (animal_id, habitat_id))
    con.commit()
    con.close()

# Observaciones
def registrar_observacion(animal_id, lugar, observador):
    con = conectar()
    cur = con.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO observaciones(animal_id, fecha, lugar, observador) VALUES (?, ?, ?, ?)",
                (animal_id, fecha, lugar, observador))
    con.commit()
    con.close()

def listar_observaciones():
    con = conectar()
    cur = con.cursor()
    cur.execute('''
    SELECT a.nombre_comun, o.lugar, o.fecha, o.observador
    FROM observaciones o
    JOIN animales a ON o.animal_id = a.id
    ORDER BY o.fecha DESC
    ''')
    return cur.fetchall()

def ver_animales_con_habitats():
    con = conectar()
    cur = con.cursor()
    cur.execute('''
    SELECT a.nombre_comun, a.nivel_peligro,
           GROUP_CONCAT(h.nombre, ', ') AS habitats
    FROM animales a
    LEFT JOIN animales_habitats ah ON a.id = ah.animal_id
    LEFT JOIN habitats h ON ah.habitat_id = h.id
    GROUP BY a.id
    ''')
    return cur.fetchall()

# Uso de ejemplo
if __name__ == "__main__":
    crear_tablas()

    agregar_animal("Jaguar", "Panthera onca", "En Peligro")
    agregar_animal("Rana Dorada", "Atelopus zeteki", "Críticamente Amenazado")

    agregar_habitat("Selva Tropical", "Bosques húmedos tropicales con alta biodiversidad")
    agregar_habitat("Riachuelos Montañosos", "Cuerpos de agua en zonas altas, frescas")

    asignar_habitat_a_animal(1, 1)
    asignar_habitat_a_animal(2, 2)

    registrar_observacion(1, "Parque Nacional Darién", "Bióloga Ana Pérez")
    registrar_observacion(2, "Altos de Campana", "Guardaparque Roberto")

    print("Animales con sus hábitats:")
    for a in ver_animales_con_habitats():
        print(f"{a[0]} | Peligro: {a[1]} | Hábitats: {a[2]}")

    print("\nObservaciones recientes:")
    for obs in listar_observaciones():
        print(f"{obs[0]} fue visto en {obs[1]} por {obs[3]} el {obs[2]}")