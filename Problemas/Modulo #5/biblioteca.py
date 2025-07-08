import json
import os
import uuid
from typing import Dict, List, Optional, Any
import redis
from dotenv import load_dotenv
from colorama import init, Fore, Style
from tabulate import tabulate

# Inicializar colorama
init(autoreset=True)

# Cargar variables de entorno
load_dotenv()

# Configuración de conexión KeyDB
KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
KEYDB_PORT = int(os.getenv("KEYDB_PORT", "6379"))
KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD", "")

# Inicializar cliente Redis (KeyDB es compatible con Redis)
try:
    db = redis.Redis(
        host=KEYDB_HOST,
        port=KEYDB_PORT,
        password=KEYDB_PASSWORD,
        decode_responses=True
    )
    db.ping()
    print(Fore.GREEN + "¡Conexión exitosa a KeyDB!")
except redis.ConnectionError:
    print(Fore.RED + "Error al conectar a KeyDB. Por favor, verifica tu configuración de conexión.")
    exit(1)


class Libro:
    def __init__(self, titulo: str, autor: str, genero: str, estado_lectura: bool, libro_id: Optional[str] = None):
        self.id = libro_id or str(uuid.uuid4())
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.estado_lectura = estado_lectura

    def a_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero,
            "estado_lectura": self.estado_lectura
        }

    @classmethod
    def desde_dict(cls, datos: Dict[str, Any]) -> 'Libro':
        return cls(
            titulo=datos["titulo"],
            autor=datos["autor"],
            genero=datos["genero"],
            estado_lectura=datos["estado_lectura"],
            libro_id=datos["id"]
        )

# Función para verificar la conexión a KeyDB
def verificar_conexion() -> bool:
    try:
        db.ping()
        return True
    except:
        print(Fore.RED + "Error de conexión con KeyDB. Intente nuevamente.")
        return False

# Operaciones CRUD
def agregar_libro(libro: Libro) -> bool:
    # Validar conexión antes de proceder
    if not verificar_conexion():
        return False

    # Verificar que el libro no sea duplicado por título
    libros = listar_todos_libros()
    for l in libros:
        if l.titulo.lower() == libro.titulo.lower() and l.autor.lower() == libro.autor.lower():
            print(Fore.YELLOW + "Ya existe un libro con el mismo título y autor.")
            confirmacion = input("¿Desea agregarlo de todos modos? (si/no): ").lower()
            if confirmacion not in ["si", "s", "yes", "y"]:
                return False

    try:
        datos_libro = json.dumps(libro.a_dict())
        db.set(f"libro:{libro.id}", datos_libro)
        return True
    except Exception as e:
        print(Fore.RED + f"Error al agregar libro: {e}")
        return False

def obtener_libro(libro_id: str) -> Optional[Libro]:
    if not verificar_conexion():
        return None

    if not libro_id or not libro_id.strip():
        print(Fore.YELLOW + "ID de libro no válido.")
        return None

    try:
        datos_libro = db.get(f"libro:{libro_id}")
        if datos_libro:
            return Libro.desde_dict(json.loads(datos_libro))
        return None
    except json.JSONDecodeError:
        print(Fore.RED + "Error al decodificar datos del libro.")
        return None
    except Exception as e:
        print(Fore.RED + f"Error al recuperar libro: {e}")
        return None

def actualizar_libro(libro: Libro) -> bool:
    if not verificar_conexion():
        return False

    try:
        if not libro.id or not db.exists(f"libro:{libro.id}"):
            print(Fore.YELLOW + f"El libro con ID {libro.id} no existe.")
            return False

        datos_libro = json.dumps(libro.a_dict())
        db.set(f"libro:{libro.id}", datos_libro)
        return True
    except Exception as e:
        print(Fore.RED + f"Error al actualizar libro: {e}")
        return False

def eliminar_libro(libro_id: str) -> bool:
    if not verificar_conexion():
        return False

    if not libro_id or not libro_id.strip():
        print(Fore.YELLOW + "ID de libro no válido.")
        return False

    try:
        if not db.exists(f"libro:{libro_id}"):
            print(Fore.YELLOW + f"El libro con ID {libro_id} no existe.")
            return False

        db.delete(f"libro:{libro_id}")
        return True
    except Exception as e:
        print(Fore.RED + f"Error al eliminar libro: {e}")
        return False

def listar_todos_libros() -> List[Libro]:
    libros = []

    if not verificar_conexion():
        return libros

    try:
        cursor = 0
        while True:
            cursor, keys = db.scan(cursor=cursor, match="libro:*", count=100)
            for key in keys:
                try:
                    datos_libro = db.get(key)
                    if datos_libro:
                        libros.append(Libro.desde_dict(json.loads(datos_libro)))
                except json.JSONDecodeError:
                    print(Fore.YELLOW + f"Error al decodificar datos del libro con clave {key}.")
                except Exception as e:
                    print(Fore.YELLOW + f"Error al procesar libro: {e}")

            if cursor == 0:
                break

        return libros
    except Exception as e:
        print(Fore.RED + f"Error al listar libros: {e}")
        return []

def buscar_libros(campo: str, consulta: str) -> List[Libro]:
    if not consulta or not consulta.strip():
        print(Fore.YELLOW + "El término de búsqueda no puede estar vacío.")
        return []

    libros = listar_todos_libros()
    consulta = consulta.lower()

    if campo == "titulo":
        return [libro for libro in libros if consulta in libro.titulo.lower()]
    elif campo == "autor":
        return [libro for libro in libros if consulta in libro.autor.lower()]
    elif campo == "genero":
        return [libro for libro in libros if consulta in libro.genero.lower()]
    else:
        print(Fore.YELLOW + f"Campo de búsqueda inválido: {campo}")
        return []

# Funciones auxiliares
def mostrar_libros(libros: List[Libro]) -> None:
    if not libros:
        print(Fore.YELLOW + "No se encontraron libros.")
        return

    # Preparar datos para tabulate
    datos_tabla = []
    for libro in libros:
        estado = "Sí" if libro.estado_lectura else "No"
        datos_tabla.append([libro.id[:8], libro.titulo, libro.autor, libro.genero, estado])

    # Mostrar tabla con tabulate
    headers = ["ID", "Título", "Autor", "Género", "Leído"]
    print("\n" + Fore.CYAN + tabulate(datos_tabla, headers=headers, tablefmt="grid"))

def obtener_datos_libro(libro_existente: Optional[Libro] = None) -> Optional[Libro]:
    if libro_existente:
        print(Fore.CYAN + f"Actualizando libro: {libro_existente.titulo} de {libro_existente.autor}")

        # Solicitar y validar título
        while True:
            titulo = input(f"Título [{libro_existente.titulo}]: ") or libro_existente.titulo
            if titulo.strip():
                break
            print(Fore.YELLOW + "El título no puede estar vacío.")

        # Solicitar y validar autor
        while True:
            autor = input(f"Autor [{libro_existente.autor}]: ") or libro_existente.autor
            if autor.strip():
                break
            print(Fore.YELLOW + "El autor no puede estar vacío.")

        # Solicitar y validar género
        while True:
            genero = input(f"Género [{libro_existente.genero}]: ") or libro_existente.genero
            if genero.strip():
                break
            print(Fore.YELLOW + "El género no puede estar vacío.")

        # Validar estado de lectura
        while True:
            estado_input = input(f"Leído (si/no) [{'si' if libro_existente.estado_lectura else 'no'}]: ").lower() or (
                'si' if libro_existente.estado_lectura else 'no')
            if estado_input in ["si", "s", "yes", "y", "true", "t", "1", "no", "n", "false", "f", "0"]:
                estado_lectura = estado_input in ["si", "s", "yes", "y", "true", "t", "1"]
                break
            print(Fore.YELLOW + "Valor inválido. Use 'si' o 'no'.")

        return Libro(titulo, autor, genero, estado_lectura, libro_existente.id)
    else:
        # Solicitar y validar título
        while True:
            titulo = input("Título: ")
            if titulo.strip():
                break
            print(Fore.YELLOW + "El título no puede estar vacío.")

        # Solicitar y validar autor
        while True:
            autor = input("Autor: ")
            if autor.strip():
                break
            print(Fore.YELLOW + "El autor no puede estar vacío.")

        # Solicitar y validar género
        while True:
            genero = input("Género: ")
            if genero.strip():
                break
            print(Fore.YELLOW + "El género no puede estar vacío.")

        # Validar estado de lectura
        while True:
            estado_input = input("Leído (si/no): ").lower()
            if estado_input in ["si", "s", "yes", "y", "true", "t", "1", "no", "n", "false", "f", "0"]:
                estado_lectura = estado_input in ["si", "s", "yes", "y", "true", "t", "1"]
                break
            print(Fore.YELLOW + "Valor inválido. Use 'si' o 'no'.")

        return Libro(titulo, autor, genero, estado_lectura)

def seleccionar_libro() -> Optional[str]:
    libros = listar_todos_libros()
    if not libros:
        print(Fore.YELLOW + "No hay libros en la biblioteca.")
        return None

    mostrar_libros(libros)

    libro_id = input("Ingresa el ID del libro (o 'q' para cancelar): ")
    if libro_id.lower() == 'q':
        return None

    # Verificar si el ID es válido
    for libro in libros:
        if libro.id.startswith(libro_id):
            return libro.id

    print(Fore.YELLOW + "Libro no encontrado.")
    return None

# Menú principal
def menu_principal():
    while True:
        print("\n" + Fore.CYAN + Style.BRIGHT + "=== Biblioteca Personal ===")
        print(Fore.WHITE + "1. Agregar un nuevo libro")
        print(Fore.WHITE + "2. Actualizar un libro")
        print(Fore.WHITE + "3. Eliminar un libro")
        print(Fore.WHITE + "4. Listar todos los libros")
        print(Fore.WHITE + "5. Buscar libros")
        print(Fore.WHITE + "6. Salir")
        try:
            opcion = input("\n" + Fore.CYAN + "Ingresa tu opción (1-6): ")
            # Validar que la opción sea un número del 1 al 6
            if not opcion.isdigit() or int(opcion) < 1 or int(opcion) > 6:
                print(Fore.YELLOW + "Opción inválida. Por favor, ingresa un número del 1 al 6.")
                continue
            opcion = int(opcion)
            if opcion == 1:
                libro = obtener_datos_libro()
                if libro and agregar_libro(libro):
                    print(Fore.GREEN + f"¡Libro '{libro.titulo}' agregado exitosamente!")

            elif opcion == 2:
                libro_id = seleccionar_libro()
                if libro_id:
                    libro = obtener_libro(libro_id)
                    if libro:
                        libro_actualizado = obtener_datos_libro(libro)
                        if libro_actualizado and actualizar_libro(libro_actualizado):
                            print(Fore.GREEN + f"¡Libro '{libro_actualizado.titulo}' actualizado exitosamente!")
            elif opcion == 3:
                libro_id = seleccionar_libro()
                if libro_id:
                    libro = obtener_libro(libro_id)
                    if libro:
                        while True:
                            confirmar = input(f"¿Estás seguro de que deseas eliminar '{libro.titulo}'? (si/no): ")
                            if confirmar.lower() in ["si", "s", "yes", "y", "no", "n"]:
                                break
                            print(Fore.YELLOW + "Respuesta inválida. Responda con 'si' o 'no'.")

                        if confirmar.lower() in ["si", "s", "yes", "y"]:
                            if eliminar_libro(libro_id):
                                print(Fore.GREEN + "¡Libro eliminado exitosamente!")
            elif opcion == 4:
                libros = listar_todos_libros()
                mostrar_libros(libros)
            elif opcion == 5:
                print("\n" + Fore.CYAN + "=== Buscar Libros ===")
                print(Fore.WHITE + "1. Buscar por título")
                print(Fore.WHITE + "2. Buscar por autor")
                print(Fore.WHITE + "3. Buscar por género")
                while True:
                    opcion_busqueda = input("\n" + Fore.CYAN + "Ingresa tu opción (1-3): ")
                    if opcion_busqueda in ["1", "2", "3"]:
                        break
                    print(Fore.YELLOW + "Opción inválida. Por favor, ingresa un número del 1 al 3.")

                consulta = input("Ingresa término de búsqueda: ")
                while not consulta.strip():
                    print(Fore.YELLOW + "El término de búsqueda no puede estar vacío.")
                    consulta = input("Ingresa término de búsqueda: ")

                if opcion_busqueda == "1":
                    libros = buscar_libros("titulo", consulta)
                elif opcion_busqueda == "2":
                    libros = buscar_libros("autor", consulta)
                elif opcion_busqueda == "3":
                    libros = buscar_libros("genero", consulta)
                mostrar_libros(libros)
            elif opcion == 6:
                print(Fore.GREEN + "Saliendo de la aplicación. ¡Hasta pronto!")
                break
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nOperación cancelada por el usuario.")
            respuesta = input("¿Desea salir de la aplicación? (si/no): ").lower()
            if respuesta in ["si", "s", "yes", "y"]:
                print(Fore.GREEN + "Saliendo de la aplicación. ¡Hasta pronto!")
                break
        except Exception as e:
            print(Fore.RED + f"Error inesperado: {e}")
if __name__ == "__main__":
    menu_principal()