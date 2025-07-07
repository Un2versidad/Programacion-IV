import sys
import time
from gestor_libros import GestorLibros
from tabulate import tabulate
from colorama import init, Fore, Back, Style
from pyfiglet import Figlet
from tqdm import tqdm

# Inicializar colorama
init(autoreset=True)

def validar_campo(campo, nombre_campo):
    """Valida que un campo no esté vacío o solo contenga espacios"""
    if not campo or campo.strip() == "":
        print(Fore.RED + f"Error: El campo {nombre_campo} no puede estar vacío.")
        return False
    return True

def mostrar_titulo():
    """Muestra un título ASCII art para la aplicación"""
    fig = Figlet(font='slant')
    titulo = fig.renderText('Biblioteca Personal')
    print(Fore.CYAN + titulo)
    print(Fore.YELLOW + "=" * 60)
    print(Fore.WHITE + Style.BRIGHT + "Sistema de Gestión de Libros".center(60))
    print(Fore.YELLOW + "=" * 60 + "\n")

def mostrar_menu_estado_lectura():
    """Muestra un menú para seleccionar el estado de lectura"""
    print(Fore.CYAN + "\n--- SELECCIONE ESTADO DE LECTURA ---")
    print(Fore.GREEN + "1. " + Fore.WHITE + "Leído")
    print(Fore.RED + "2. " + Fore.WHITE + "No leído")
    print(Fore.YELLOW + "3. " + Fore.WHITE + "En progreso")

    while True:
        opcion = input(Fore.YELLOW + "Ingrese opción (1-3): " + Fore.WHITE)
        if opcion == '1':
            return "Leído"
        elif opcion == '2':
            return "No leído"
        elif opcion == '3':
            return "En progreso"
        else:
            print(Fore.RED + "Opción inválida. Intente de nuevo.")

def imprimir_menu():
    """Muestra el menú principal con colores"""
    print(Fore.CYAN + "\n--- MENÚ PRINCIPAL ---")
    print(Fore.GREEN + "1. " + Fore.WHITE + "Agregar un nuevo libro")
    print(Fore.GREEN + "2. " + Fore.WHITE + "Actualizar información de libro")
    print(Fore.GREEN + "3. " + Fore.WHITE + "Eliminar un libro")
    print(Fore.GREEN + "4. " + Fore.WHITE + "Listar todos los libros")
    print(Fore.GREEN + "5. " + Fore.WHITE + "Buscar libros")
    print(Fore.RED + "6. " + Fore.WHITE + "Salir")
    return input(Fore.YELLOW + "Ingrese su opción (1-6): " + Fore.WHITE)

def menu_agregar_libro(gestor_libros):
    """Menú para agregar un nuevo libro"""
    print(Fore.CYAN + "\n--- AGREGAR UN NUEVO LIBRO ---")

    # Validar título
    while True:
        titulo = input(Fore.YELLOW + "Ingrese título del libro: " + Fore.WHITE)
        if validar_campo(titulo, "título"):
            break

    # Validar autor
    while True:
        autor = input(Fore.YELLOW + "Ingrese nombre del autor: " + Fore.WHITE)
        if validar_campo(autor, "autor"):
            break

    # Validar género
    while True:
        genero = input(Fore.YELLOW + "Ingrese género: " + Fore.WHITE)
        if validar_campo(genero, "género"):
            break

    # Usar menú para seleccionar estado de lectura
    print(Fore.YELLOW + "Seleccione el estado de lectura del libro:")
    estado_lectura = mostrar_menu_estado_lectura()

    # Agregar libro a la base de datos con animación
    print(Fore.CYAN + "Agregando libro a la base de datos...")
    for _ in tqdm(range(10), desc="Progreso", bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)):
        time.sleep(0.1)

    try:
        id_libro = gestor_libros.agregar_libro(titulo, autor, genero, estado_lectura)
        print(Fore.GREEN + f"✓ Libro agregado exitosamente con ID: {id_libro}")
    except Exception as e:
        print(Fore.RED + f"✗ Error al agregar libro: {e}")

def mostrar_tabla_libros(libros, titulo_tabla="Libros"):
    """Muestra una tabla formateada de libros usando tabulate"""
    if not libros:
        print(Fore.YELLOW + "No se encontraron libros en la biblioteca.")
        return False

    # Preparar datos para la tabla
    tabla_datos = []
    for i, libro in enumerate(libros, 1):
        estado = libro['estado_lectura']
        color_estado = ""
        if estado.lower() == "leído":
            color_estado = Fore.GREEN + estado + Fore.RESET
        elif estado.lower() == "no leído":
            color_estado = Fore.RED + estado + Fore.RESET
        else:  # En progreso
            color_estado = Fore.YELLOW + estado + Fore.RESET

        tabla_datos.append([
            i,
            libro['_id'],
            libro['titulo'],
            libro['autor'],
            libro['genero'],
            color_estado
        ])

    # Mostrar tabla
    print(Fore.CYAN + f"\n--- {titulo_tabla.upper()} ---")
    print(tabulate(
        tabla_datos,
        headers=[Fore.BLUE + "Nº", "ID", "Título", "Autor", "Género", "Estado" + Fore.RESET],
        tablefmt="fancy_grid"
    ))
    return True

def menu_actualizar_libro(gestor_libros):
    """Menú para actualizar información de un libro"""
    print(Fore.CYAN + "\n--- ACTUALIZAR INFORMACIÓN DE LIBRO ---")

    # Listar todos los libros
    libros = gestor_libros.listar_libros()
    if not mostrar_tabla_libros(libros):
        return

    # Obtener libro a actualizar
    try:
        seleccion = int(input(Fore.YELLOW + "\nIngrese el número del libro a actualizar: " + Fore.WHITE))
        if seleccion < 1 or seleccion > len(libros):
            print(Fore.RED + "Selección inválida.")
            return

        libro = libros[seleccion - 1]
        id_libro = libro['_id']

        # Obtener información actualizada
        print(Fore.MAGENTA + f"\nActualizando: {libro['titulo']} por {libro['autor']}")
        print(Fore.YELLOW + "(Dejar en blanco para mantener el valor actual)")

        titulo = input(Fore.YELLOW + f"Nuevo título [{libro['titulo']}]: " + Fore.WHITE) or None
        autor = input(Fore.YELLOW + f"Nuevo autor [{libro['autor']}]: " + Fore.WHITE) or None
        genero = input(Fore.YELLOW + f"Nuevo género [{libro['genero']}]: " + Fore.WHITE) or None

        # Preguntar si desea actualizar el estado
        actualizar_estado = input(
            Fore.YELLOW + f"¿Desea cambiar el estado actual [{libro['estado_lectura']}]? (s/n): " + Fore.WHITE)
        estado_lectura = None
        if actualizar_estado.lower() == 's':
            estado_lectura = mostrar_menu_estado_lectura()

        # Actualizar libro con animación
        print(Fore.CYAN + "Actualizando libro...")
        for _ in tqdm(range(10), desc="Progreso", bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)):
            time.sleep(0.1)

        if gestor_libros.actualizar_libro(id_libro, titulo, autor, genero, estado_lectura):
            print(Fore.GREEN + "✓ Libro actualizado exitosamente.")
        else:
            print(Fore.YELLOW + "ℹ No se realizaron cambios.")
    except ValueError:
        print(Fore.RED + "✗ Por favor ingrese un número válido.")
    except Exception as e:
        print(Fore.RED + f"✗ Error al actualizar libro: {e}")

def menu_eliminar_libro(gestor_libros):
    """Menú para eliminar un libro"""
    print(Fore.CYAN + "\n--- ELIMINAR UN LIBRO ---")

    # Listar todos los libros
    libros = gestor_libros.listar_libros()
    if not mostrar_tabla_libros(libros):
        return

    # Obtener libro a eliminar
    try:
        seleccion = int(input(Fore.YELLOW + "\nIngrese el número del libro a eliminar: " + Fore.WHITE))
        if seleccion < 1 or seleccion > len(libros):
            print(Fore.RED + "Selección inválida.")
            return

        libro = libros[seleccion - 1]

        # Confirmar eliminación
        print(
            Fore.RED + Back.WHITE + Style.BRIGHT + f"\n¡ADVERTENCIA! Esta acción no se puede deshacer." + Style.RESET_ALL)
        confirmar = input(
            Fore.RED + f"¿Está seguro que desea eliminar '{libro['titulo']}' por {libro['autor']}? (s/n): " + Fore.WHITE)
        if confirmar.lower() != 's':
            print(Fore.YELLOW + "Eliminación cancelada.")
            return

        # Eliminar libro con animación
        print(Fore.CYAN + "Eliminando libro...")
        for _ in tqdm(range(10), desc="Progreso", bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.RED, Fore.RESET)):
            time.sleep(0.1)

        if gestor_libros.eliminar_libro(libro['_id']):
            print(Fore.GREEN + "✓ Libro eliminado exitosamente.")
        else:
            print(Fore.RED + "✗ Error al eliminar libro.")
    except ValueError:
        print(Fore.RED + "✗ Por favor ingrese un número válido.")
    except Exception as e:
        print(Fore.RED + f"✗ Error al eliminar libro: {e}")

def menu_listar_libros(gestor_libros):
    """Menú para listar todos los libros"""
    # Obtener todos los libros
    libros = gestor_libros.listar_libros()
    mostrar_tabla_libros(libros, "Lista de Todos los Libros")

    if libros:
        # Mostrar estadísticas
        leidos = len([l for l in libros if l['estado_lectura'].lower() == 'leído'])
        no_leidos = len([l for l in libros if l['estado_lectura'].lower() == 'no leído'])
        en_progreso = len([l for l in libros if l['estado_lectura'].lower() == 'en progreso'])

        print(Fore.CYAN + "\n--- ESTADÍSTICAS ---")
        stats = [
            ["Total libros", len(libros)],
            [Fore.GREEN + "Leídos" + Fore.RESET, leidos],
            [Fore.RED + "No leídos" + Fore.RESET, no_leidos],
            [Fore.YELLOW + "En progreso" + Fore.RESET, en_progreso]
        ]
        print(tabulate(stats, tablefmt="simple"))

def menu_buscar_libros(gestor_libros):
    """Menú para buscar libros"""
    print(Fore.CYAN + "\n--- BUSCAR LIBROS ---")
    print(Fore.GREEN + "1. " + Fore.WHITE + "Buscar en todos los campos")
    print(Fore.GREEN + "2. " + Fore.WHITE + "Buscar por título")
    print(Fore.GREEN + "3. " + Fore.WHITE + "Buscar por autor")
    print(Fore.GREEN + "4. " + Fore.WHITE + "Buscar por género")
    opcion_busqueda = input(Fore.YELLOW + "Ingrese opción de búsqueda (1-4): " + Fore.WHITE)

    campo = None
    if opcion_busqueda == '2':
        campo = "titulo"
    elif opcion_busqueda == '3':
        campo = "autor"
    elif opcion_busqueda == '4':
        campo = "genero"

    consulta = input(Fore.YELLOW + "Ingrese término de búsqueda: " + Fore.WHITE)

    if not consulta:
        print(Fore.RED + "El término de búsqueda no puede estar vacío.")
        return

    # Animación de búsqueda
    print(Fore.CYAN + "Buscando libros...")
    for _ in tqdm(range(5), desc="Progreso", bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)):
        time.sleep(0.2)

    resultados = gestor_libros.buscar_libros(consulta, campo)

    if not resultados:
        print(Fore.YELLOW + f"No se encontraron libros que coincidan con '{consulta}'.")
        return

    print(Fore.GREEN + f"Se encontraron {len(resultados)} libros coincidentes:")
    mostrar_tabla_libros(resultados, f"Resultados para '{consulta}'")

def principal():
    """Función principal del programa"""
    # Limpiar pantalla
    print("\033[2J\033[H", end="")

    # Mostrar título de la aplicación
    mostrar_titulo()

    # Inicializar gestor de libros con animación
    print(Fore.CYAN + "Conectando a la base de datos...")
    for _ in tqdm(range(10), desc="Progreso", bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)):
        time.sleep(0.1)

    try:
        gestor_libros = GestorLibros()
        print(Fore.GREEN + "✓ Conexión a MongoDB exitosa.")
    except ConnectionError as e:
        print(Fore.RED + f"✗ Error: {e}")
        sys.exit(1)

    while True:
        opcion = imprimir_menu()

        if opcion == '1':
            menu_agregar_libro(gestor_libros)
        elif opcion == '2':
            menu_actualizar_libro(gestor_libros)
        elif opcion == '3':
            menu_eliminar_libro(gestor_libros)
        elif opcion == '4':
            menu_listar_libros(gestor_libros)
        elif opcion == '5':
            menu_buscar_libros(gestor_libros)
        elif opcion == '6':
            # Confirmar salida
            confirmar_salida = input(Fore.YELLOW + "¿Está seguro que desea salir? (s/n): " + Fore.WHITE)
            if confirmar_salida.lower() != 's':
                continue

            print(Fore.CYAN + "\nCerrando aplicación...", flush=True)
            for _ in tqdm(range(5), desc="Progreso", bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)):
                time.sleep(0.2)
            print(Fore.YELLOW + Style.BRIGHT + "\n¡Gracias por usar el Sistema de Gestión de Biblioteca Personal!",
                  flush=True)
            print(Fore.MAGENTA + "¡Hasta pronto!" + Style.RESET_ALL, flush=True)
            break
        else:
            print(Fore.RED + "Opción inválida. Por favor intente de nuevo.")

if __name__ == "__main__":
    principal()