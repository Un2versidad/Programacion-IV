import sqlite3
import os
import sys
from tabulate import tabulate
from colorama import init, Fore, Style
from contextlib import contextmanager

init(autoreset=True)

class DatabaseManager:
    DB_FILE = 'academia.db'

    @contextmanager
    def connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.DB_FILE)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error de base de datos: {e}{Style.RESET_ALL}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def initialize_db(self):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Profesores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    especialidad TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cursos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    id_profesor INTEGER,
                    FOREIGN KEY (id_profesor) REFERENCES Profesores(id)
                    ON DELETE SET NULL
                )
            ''')
            conn.commit()

    def agregar_profesor(self, nombre, especialidad):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Profesores (nombre, especialidad) VALUES (?, ?)",
                (nombre, especialidad)
            )
            conn.commit()
            return cursor.lastrowid

    def actualizar_profesor(self, id_profesor, nombre, especialidad):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Profesores SET nombre = ?, especialidad = ? WHERE id = ?",
                (nombre, especialidad, id_profesor)
            )
            conn.commit()
            return cursor.rowcount > 0

    def eliminar_profesor(self, id_profesor):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Profesores WHERE id = ?", (id_profesor,))
            conn.commit()
            return cursor.rowcount > 0

    def lista_profesores(self):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, especialidad FROM Profesores ORDER BY nombre")
            return [dict(row) for row in cursor.fetchall()]

    def get_profesor(self, id_profesor):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Profesores WHERE id = ?", (id_profesor,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def agregar_curso(self, titulo, id_profesor):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cursos (titulo, id_profesor) VALUES (?, ?)",
                (titulo, id_profesor)
            )
            conn.commit()
            return cursor.lastrowid

    def lista_cursos(self):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.id, c.titulo, c.id_profesor, p.nombre as nombre_profesor
                FROM cursos c
                LEFT JOIN Profesores p ON c.id_profesor = p.id
                ORDER BY c.titulo
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def eliminar_curso(self, id_curso):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cursos WHERE id = ?", (id_curso,))
            conn.commit()
            return cursor.rowcount > 0

    def cursos_por_profesor(self, id_profesor):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, titulo FROM cursos WHERE id_profesor = ? ORDER BY titulo",
                (id_profesor,)
            )
            return [dict(row) for row in cursor.fetchall()]

class Academia:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.initialize_db()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        self.clear_screen()
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 50}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(50)}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 50}{Style.RESET_ALL}\n")

    def input_with_validation(self, prompt, validation_func=None, error_msg=None):
        while True:
            value = input(f"{Fore.YELLOW}{prompt}: {Style.RESET_ALL}")
            if not validation_func or validation_func(value):
                return value
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")

    def mostrar_profesores(self):
        profesores = self.db.lista_profesores()

        if not profesores:
            print(f"{Fore.YELLOW}No hay profesores registrados.{Style.RESET_ALL}")
            return

        headers = ["ID", "Nombre", "Especialidad"]
        data = [[p['id'], p['nombre'], p['especialidad']] for p in profesores]

        print(f"\n{Fore.GREEN}Lista de Profesores:{Style.RESET_ALL}")
        print(tabulate(data, headers=headers, tablefmt="pretty"))

    def mostrar_cursos(self):
        cursos = self.db.lista_cursos()

        if not cursos:
            print(f"{Fore.YELLOW}No hay cursos registrados.{Style.RESET_ALL}")
            return

        headers = ["ID", "Título", "Profesor"]
        data = [[c['id'], c['titulo'], c['nombre_profesor'] or 'Sin asignar'] for c in cursos]

        print(f"\n{Fore.GREEN}Lista de Cursos:{Style.RESET_ALL}")
        print(tabulate(data, headers=headers, tablefmt="pretty"))

    def agregar_profesor_ui(self):
        self.print_header("AGREGAR PROFESOR")

        nombre = self.input_with_validation(
            "Nombre del profesor",
            lambda x: x.strip(),
            "El nombre no puede estar vacío"
        )

        especialidad = self.input_with_validation(
            "Especialidad del profesor",
            lambda x: x.strip(),
            "La especialidad no puede estar vacía"
        )

        try:
            id_profesor = self.db.agregar_profesor(nombre.strip(), especialidad.strip())
            print(f"\n{Fore.GREEN}Profesor agregado exitosamente con ID: {id_profesor}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error al agregar profesor: {e}{Style.RESET_ALL}")

        input("\nPresione Enter para continuar...")

    def actualizar_profesor_ui(self):
        self.print_header("ACTUALIZAR PROFESOR")
        self.mostrar_profesores()

        try:
            id_profesor = int(self.input_with_validation(
                "\nID del profesor a actualizar",
                lambda x: x.isdigit() and int(x) > 0,
                "Por favor, ingrese un ID válido (número entero positivo)"
            ))

            profesor = self.db.get_profesor(id_profesor)
            if not profesor:
                print(f"{Fore.RED}No se encontró un profesor con ese ID.{Style.RESET_ALL}")
                input("\nPresione Enter para continuar...")
                return

            print(f"\n{Fore.CYAN}Actualizando profesor: {profesor['nombre']}{Style.RESET_ALL}")

            nombre = self.input_with_validation(
                f"Nuevo nombre (actual: {profesor['nombre']}) [Enter para mantener]",
            )
            if not nombre.strip():
                nombre = profesor['nombre']

            especialidad = self.input_with_validation(
                f"Nueva especialidad (actual: {profesor['especialidad']}) [Enter para mantener]",
            )
            if not especialidad.strip():
                especialidad = profesor['especialidad']

            if self.db.actualizar_profesor(id_profesor, nombre.strip(), especialidad.strip()):
                print(f"\n{Fore.GREEN}Profesor actualizado exitosamente.{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}No se realizaron cambios.{Style.RESET_ALL}")

        except ValueError:
            print(f"{Fore.RED}ID inválido.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error al actualizar profesor: {e}{Style.RESET_ALL}")

        input("\nPresione Enter para continuar...")

    def eliminar_profesor_ui(self):
        self.print_header("ELIMINAR PROFESOR")
        self.mostrar_profesores()

        try:
            id_profesor = int(self.input_with_validation(
                "\nID del profesor a eliminar",
                lambda x: x.isdigit() and int(x) > 0,
                "Por favor, ingrese un ID válido (número entero positivo)"
            ))

            profesor = self.db.get_profesor(id_profesor)
            if not profesor:
                print(f"{Fore.RED}No se encontró un profesor con ese ID.{Style.RESET_ALL}")
                input("\nPresione Enter para continuar...")
                return

            cursos = self.db.cursos_por_profesor(id_profesor)
            if cursos:
                print(f"\n{Fore.YELLOW}Advertencia: Este profesor tiene {len(cursos)} curso(s) asignado(s).{Style.RESET_ALL}")
                print("Si elimina al profesor, estos cursos quedarán sin profesor asignado.")

            confirmacion = input(f"\n{Fore.RED}¿Está seguro de eliminar al profesor {profesor['nombre']}? (s/n): {Style.RESET_ALL}").lower()

            if confirmacion == 's':
                if self.db.eliminar_profesor(id_profesor):
                    print(f"\n{Fore.GREEN}Profesor eliminado exitosamente.{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}No se pudo eliminar el profesor.{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}Operación cancelada.{Style.RESET_ALL}")

        except ValueError:
            print(f"{Fore.RED}ID inválido.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error al eliminar profesor: {e}{Style.RESET_ALL}")

        input("\nPresione Enter para continuar...")

    def agregar_curso_ui(self):
        self.print_header("AGREGAR CURSO")

        titulo = self.input_with_validation(
            "Título del curso",
            lambda x: x.strip(),
            "El título no puede estar vacío"
        )

        self.mostrar_profesores()

        try:
            id_profesor = self.input_with_validation(
                "\nID del profesor que imparte el curso (0 para dejar sin asignar)",
                lambda x: x.isdigit(),
                "Por favor, ingrese un ID válido (número entero)"
            )

            id_profesor = int(id_profesor)
            if id_profesor > 0 and not self.db.get_profesor(id_profesor):
                print(f"{Fore.RED}No se encontró un profesor con ese ID.{Style.RESET_ALL}")
                input("\nPresione Enter para continuar...")
                return

            id_profesor = id_profesor if id_profesor > 0 else None

            id_curso = self.db.agregar_curso(titulo.strip(), id_profesor)
            print(f"\n{Fore.GREEN}Curso agregado exitosamente con ID: {id_curso}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error al agregar curso: {e}{Style.RESET_ALL}")

        input("\nPresione Enter para continuar...")

    def eliminar_curso_ui(self):
        self.print_header("ELIMINAR CURSO")
        self.mostrar_cursos()

        try:
            id_curso = int(self.input_with_validation(
                "\nID del curso a eliminar",
                lambda x: x.isdigit() and int(x) > 0,
                "Por favor, ingrese un ID válido (número entero positivo)"
            ))

            confirmacion = input(f"\n{Fore.RED}¿Está seguro de eliminar este curso? (s/n): {Style.RESET_ALL}").lower()

            if confirmacion == 's':
                if self.db.eliminar_curso(id_curso):
                    print(f"\n{Fore.GREEN}Curso eliminado exitosamente.{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}No se encontró un curso con ese ID.{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}Operación cancelada.{Style.RESET_ALL}")

        except ValueError:
            print(f"{Fore.RED}ID inválido.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error al eliminar curso: {e}{Style.RESET_ALL}")

        input("\nPresione Enter para continuar...")

    def cursos_por_profesor_ui(self):
        self.print_header("CURSOS POR PROFESOR")
        self.mostrar_profesores()

        try:
            id_profesor = int(self.input_with_validation(
                "\nID del profesor",
                lambda x: x.isdigit() and int(x) > 0,
                "Por favor, ingrese un ID válido (número entero positivo)"
            ))

            profesor = self.db.get_profesor(id_profesor)
            if not profesor:
                print(f"{Fore.RED}No se encontró un profesor con ese ID.{Style.RESET_ALL}")
                input("\nPresione Enter para continuar...")
                return

            cursos = self.db.cursos_por_profesor(id_profesor)

            print(f"\n{Fore.GREEN}Cursos impartidos por {profesor['nombre']}:{Style.RESET_ALL}")

            if not cursos:
                print(f"{Fore.YELLOW}Este profesor no tiene cursos asignados.{Style.RESET_ALL}")
            else:
                headers = ["ID", "Título"]
                data = [[c['id'], c['titulo']] for c in cursos]
                print(tabulate(data, headers=headers, tablefmt="pretty"))

        except ValueError:
            print(f"{Fore.RED}ID inválido.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error al consultar cursos: {e}{Style.RESET_ALL}")

        input("\nPresione Enter para continuar...")

    def ejecutar(self):
        while True:
            self.print_header("SISTEMA DE GESTIÓN ACADÉMICA")

            menu_options = [
                (1, "Agregar Profesor"),
                (2, "Actualizar Profesor"),
                (3, "Eliminar Profesor"),
                (4, "Listar Profesores"),
                (5, "Agregar Curso"),
                (6, "Listar Cursos"),
                (7, "Eliminar Curso"),
                (8, "Ver Cursos por Profesor"),
                (0, "Salir")
            ]

            for num, desc in menu_options:
                print(f"{Fore.CYAN}{num}.{Style.RESET_ALL} {desc}")

            try:
                opcion = int(self.input_with_validation(
                    f"\n{Fore.GREEN}Seleccione una opción{Style.RESET_ALL}",
                    lambda x: x.isdigit() and 0 <= int(x) <= 8,
                    "Opción inválida. Ingrese un número del 0 al 8."
                ))

                if opcion == 0:
                    self.print_header("¡HASTA PRONTO!")
                    print(f"{Fore.GREEN}Gracias por usar el Sistema de Gestión Académica{Style.RESET_ALL}")
                    break
                elif opcion == 1:
                    self.agregar_profesor_ui()
                elif opcion == 2:
                    self.actualizar_profesor_ui()
                elif opcion == 3:
                    self.eliminar_profesor_ui()
                elif opcion == 4:
                    self.print_header("LISTA DE PROFESORES")
                    self.mostrar_profesores()
                    input("\nPresione Enter para continuar...")
                elif opcion == 5:
                    self.agregar_curso_ui()
                elif opcion == 6:
                    self.print_header("LISTA DE CURSOS")
                    self.mostrar_cursos()
                    input("\nPresione Enter para continuar...")
                elif opcion == 7:
                    self.eliminar_curso_ui()
                elif opcion == 8:
                    self.cursos_por_profesor_ui()

            except ValueError:
                print(f"{Fore.RED}Por favor, ingrese un número válido.{Style.RESET_ALL}")
                input("\nPresione Enter para continuar...")
            except Exception as e:
                print(f"{Fore.RED}Error inesperado: {e}{Style.RESET_ALL}")
                input("\nPresione Enter para continuar...")


if __name__ == '__main__':
    try:
        app = Academia()
        app.ejecutar()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Programa terminado por el usuario.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error fatal: {e}{Style.RESET_ALL}")
        sys.exit(1)