import sqlite3
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from colorama import init, Fore, Style
from tabulate import tabulate

# Inicializar colorama
init(autoreset=True)

class BaseDeDatos:
    def __init__(self, nombre_db="presupuesto.db"):
        """Inicializa la conexión a la base de datos y crea tablas si es necesario"""
        try:
            self.conexion = sqlite3.connect(nombre_db)
            self.cursor = self.conexion.cursor()
            self.crear_tablas()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al conectar con la base de datos: {e}")
            raise

    def crear_tablas(self):
        """Crea las tablas necesarias si no existen"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS articulos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    cantidad REAL NOT NULL,
                    precio_unitario REAL NOT NULL,
                    descripcion TEXT,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS gastos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descripcion TEXT NOT NULL,
                    monto REAL NOT NULL,
                    categoria TEXT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.conexion.commit()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al crear tablas: {e}")
            raise

    def insertar_articulo(self, nombre, categoria, cantidad, precio_unitario, descripcion):
        """Inserta un nuevo artículo en la base de datos"""
        try:
            self.cursor.execute('''
                INSERT INTO articulos (
                    nombre,
                    categoria,
                    cantidad,
                    precio_unitario,
                    descripcion,
                    actualizado_en
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, categoria, cantidad, precio_unitario, descripcion, datetime.now()))
            self.conexion.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al insertar artículo: {e}")
            self.conexion.rollback()
            return None

    def buscar_articulos_por_nombre(self, nombre):
        """Busca artículos por nombre (coincidencia parcial)"""
        try:
            self.cursor.execute('''
                                SELECT *
                                FROM articulos
                                WHERE nombre LIKE ?
                                ''', (f'%{nombre}%',))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al buscar artículos por nombre: {e}")
            return []

    def buscar_articulos_por_categoria(self, categoria):
        """Busca artículos por categoría (coincidencia parcial)"""
        try:
            self.cursor.execute('''
                                SELECT *
                                FROM articulos
                                WHERE categoria LIKE ?
                                ''', (f'%{categoria}%',))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al buscar artículos por categoría: {e}")
            return []

    def obtener_todos_articulos(self):
        """Obtiene todos los artículos de la base de datos"""
        try:
            self.cursor.execute('SELECT * FROM articulos ORDER BY categoria, nombre')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al obtener todos los artículos: {e}")
            return []

    def obtener_articulo_por_id(self, id_articulo):
        """Obtiene un artículo por su ID"""
        try:
            self.cursor.execute('SELECT * FROM articulos WHERE id = ?', (id_articulo,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al obtener artículo por ID: {e}")
            return None

    def actualizar_articulo(self, id_articulo, nombre, categoria, cantidad, precio_unitario, descripcion):
        """Actualiza un artículo existente"""
        try:
            self.cursor.execute('''
                                UPDATE articulos
                                SET nombre          = ?,
                                    categoria       = ?,
                                    cantidad        = ?,
                                    precio_unitario = ?,
                                    descripcion     = ?,
                                    actualizado_en  = ?
                                WHERE id = ?
                                ''', (nombre, categoria, cantidad, precio_unitario, descripcion, datetime.now(),
                                      id_articulo))
            self.conexion.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al actualizar artículo: {e}")
            self.conexion.rollback()
            return False

    def eliminar_articulo(self, id_articulo):
        """Elimina un artículo por su ID"""
        try:
            self.cursor.execute('DELETE FROM articulos WHERE id = ?', (id_articulo,))
            self.conexion.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al eliminar artículo: {e}")
            self.conexion.rollback()
            return False

    def registrar_gasto(self, descripcion, monto, categoria):
        """Registra un nuevo gasto con categoría"""
        try:
            self.cursor.execute('''
                                INSERT INTO gastos (descripcion, monto, categoria, fecha)
                                VALUES (?, ?, ?, ?)
                                ''', (descripcion, monto, categoria, datetime.now()))
            self.conexion.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al registrar gasto: {e}")
            self.conexion.rollback()
            return None

    def obtener_gastos(self):
        """Obtiene todos los gastos registrados"""
        try:
            self.cursor.execute('SELECT * FROM gastos ORDER BY fecha DESC')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al obtener gastos: {e}")
            return []

    def obtener_gastos_por_categoria(self, categoria):
        """Obtiene gastos filtrados por categoría"""
        try:
            self.cursor.execute('SELECT * FROM gastos WHERE categoria = ? ORDER BY fecha DESC', (categoria,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al obtener gastos por categoría: {e}")
            return []

    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'conexion'):
            try:
                self.conexion.close()
            except sqlite3.Error as e:
                print(f"{Fore.RED}Error al cerrar la base de datos: {e}")


class AplicacionPresupuesto:
    def __init__(self):
        """Inicializa la aplicación de presupuesto"""
        self.bd = BaseDeDatos()
        self.opciones_menu = {
            "1": self.registrar_articulo,
            "2": self.buscar_articulos,
            "3": self.editar_articulo,
            "4": self.eliminar_articulo,
            "5": self.listar_todos_articulos,
            "6": self.exportar_articulos_csv,
            "7": self.registrar_gasto,
            "8": self.ver_gastos,
            "9": self.ver_gastos_por_categoria,
            "10": self.visualizar_gastos,
            "11": self.generar_reporte_presupuesto,
            "12": self.salir_aplicacion
        }
        self.ejecutando = True

    def mostrar_menu(self):
        """Muestra las opciones del menú principal"""
        print("\n" + "=" * 50)
        print(f"{Fore.CYAN}{Style.BRIGHT}SISTEMA DE GESTIÓN DE PRESUPUESTO")
        print("=" * 50)
        print(f"{Fore.YELLOW}1. Registrar nuevo artículo")
        print(f"{Fore.YELLOW}2. Buscar artículos")
        print(f"{Fore.YELLOW}3. Editar artículo")
        print(f"{Fore.YELLOW}4. Eliminar artículo")
        print(f"{Fore.YELLOW}5. Listar todos los artículos")
        print(f"{Fore.YELLOW}6. Exportar artículos a CSV")
        print(f"{Fore.YELLOW}7. Registrar gasto")
        print(f"{Fore.YELLOW}8. Ver gastos")
        print(f"{Fore.YELLOW}9. Ver gastos por categoría")
        print(f"{Fore.YELLOW}10. Visualizar gastos")
        print(f"{Fore.YELLOW}11. Generar reporte de presupuesto")
        print(f"{Fore.YELLOW}12. Salir")
        print("=" * 50)

    def obtener_entrada_usuario(self, mensaje, funcion_validacion=None, mensaje_error=None):
        """Obtiene y valida la entrada del usuario"""
        while True:
            entrada_usuario = input(f"{Fore.WHITE}{mensaje}")
            if funcion_validacion is None or funcion_validacion(entrada_usuario):
                return entrada_usuario
            print(f"{Fore.RED}{mensaje_error or 'Entrada inválida. Intente nuevamente.'}")

    def validar_no_vacio(self, valor):
        """Valida que la entrada no esté vacía"""
        return valor.strip() != ""

    def validar_numero(self, valor):
        """Valida que la entrada sea un número válido"""
        try:
            float(valor)
            return True
        except ValueError:
            return False

    def validar_numero_positivo(self, valor):
        """Valida que la entrada sea un número positivo"""
        try:
            num = float(valor)
            return num > 0
        except ValueError:
            return False

    def validar_entero_positivo(self, valor):
        """Valida que la entrada sea un entero positivo"""
        try:
            num = int(valor)
            return num > 0
        except ValueError:
            return False

    def formatear_articulos_para_tabla(self, articulos):
        """Formatea los artículos para mostrarlos en una tabla"""
        datos_tabla = []
        for articulo in articulos:
            id_articulo, nombre, categoria, cantidad, precio_unitario = articulo[0:5]
            total = cantidad * precio_unitario
            datos_tabla.append([
                id_articulo,
                nombre,
                categoria,
                f"{cantidad:,.2f}",
                f"${precio_unitario:,.2f}",
                f"${total:,.2f}"
            ])
        return datos_tabla

    def registrar_articulo(self):
        """Registra un nuevo artículo"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- REGISTRAR NUEVO ARTÍCULO ---")

        try:
            nombre = self.obtener_entrada_usuario("Nombre del artículo: ", self.validar_no_vacio,
                                                  "El nombre no puede estar vacío.")
            categoria = self.obtener_entrada_usuario("Categoría: ", self.validar_no_vacio,
                                                     "La categoría no puede estar vacía.")
            cantidad = float(self.obtener_entrada_usuario("Cantidad: ", self.validar_numero_positivo,
                                                          "La cantidad debe ser un número positivo."))
            precio_unitario = float(self.obtener_entrada_usuario("Precio unitario: $", self.validar_numero_positivo,
                                                                 "El precio debe ser un número positivo."))
            descripcion = input(f"{Fore.WHITE}Descripción (opcional): ")

            id_articulo = self.bd.insertar_articulo(nombre, categoria, cantidad, precio_unitario, descripcion)
            if id_articulo:
                print(f"\n{Fore.GREEN}✅ Artículo registrado exitosamente con ID: {id_articulo}")
            else:
                print(f"\n{Fore.RED}❌ Error al registrar el artículo. Inténtelo nuevamente.")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error durante el registro: {e}")

    def buscar_articulos(self):
        """Busca artículos por nombre o categoría"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- BUSCAR ARTÍCULOS ---")
        print(f"{Fore.YELLOW}1. Buscar por nombre")
        print(f"{Fore.YELLOW}2. Buscar por categoría")

        try:
            opcion = self.obtener_entrada_usuario("Seleccione una opción (1-2): ", lambda x: x in ["1", "2"], "Opción inválida.")
            resultados = []
            if opcion == "1":
                nombre = self.obtener_entrada_usuario("Ingrese el nombre a buscar: ")
                resultados = self.bd.buscar_articulos_por_nombre(nombre)
            else:
                categoria = self.obtener_entrada_usuario("Ingrese la categoría a buscar: ")
                resultados = self.bd.buscar_articulos_por_categoria(categoria)

            if not resultados:
                print(f"\n{Fore.YELLOW}No se encontraron artículos que coincidan con la búsqueda.")
            else:
                print(f"\n{Fore.GREEN}Se encontraron {len(resultados)} artículos:")
                datos_tabla = self.formatear_articulos_para_tabla(resultados)
                headers = ["ID", "Nombre", "Categoría", "Cantidad", "Precio Unit.", "Total"]
                print(tabulate(datos_tabla, headers=headers, tablefmt="fancy_grid"))
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error durante la búsqueda: {e}")

    def editar_articulo(self):
        """Edita un artículo existente"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- EDITAR ARTÍCULO ---")

        try:
            id_articulo = self.obtener_entrada_usuario("Ingrese el ID del artículo a editar: ",self.validar_entero_positivo,"El ID debe ser un número entero positivo.")
            articulo = self.bd.obtener_articulo_por_id(int(id_articulo))
            if not articulo:
                print(f"\n{Fore.RED}No se encontró ningún artículo con ID {id_articulo}.")
                return

            print(f"\n{Fore.CYAN}Datos actuales del artículo:")
            datos_tabla = self.formatear_articulos_para_tabla([articulo])
            headers = ["ID", "Nombre", "Categoría", "Cantidad", "Precio Unit.", "Total"]
            print(tabulate(datos_tabla, headers=headers, tablefmt="fancy_grid"))

            print(f"\n{Fore.YELLOW}Deje en blanco para mantener el valor actual")
            nombre = self.obtener_entrada_usuario(f"Nombre [{articulo[1]}]: ") or articulo[1]
            categoria = self.obtener_entrada_usuario(f"Categoría [{articulo[2]}]: ") or articulo[2]

            cantidad_str = self.obtener_entrada_usuario(f"Cantidad [{articulo[3]}]: ",lambda x: not x or self.validar_numero_positivo(x),"La cantidad debe ser un número positivo.")
            cantidad = float(cantidad_str) if cantidad_str else articulo[3]

            precio_str = self.obtener_entrada_usuario(f"Precio unitario [{articulo[4]}]: $",lambda x: not x or self.validar_numero_positivo(x),"El precio debe ser un número positivo.")
            precio_unitario = float(precio_str) if precio_str else articulo[4]

            descripcion = input(f"{Fore.WHITE}Descripción [{articulo[5] or 'N/A'}]: ") or articulo[5] or ""

            exito = self.bd.actualizar_articulo(int(id_articulo), nombre, categoria, cantidad, precio_unitario,descripcion)
            if exito:
                print(f"\n{Fore.GREEN}✅ Artículo con ID {id_articulo} actualizado exitosamente.")
            else:
                print(f"\n{Fore.RED}❌ Error al actualizar el artículo con ID {id_articulo}.")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error durante la edición: {e}")

    def eliminar_articulo(self):
        """Elimina un artículo"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- ELIMINAR ARTÍCULO ---")

        try:
            id_articulo = self.obtener_entrada_usuario("Ingrese el ID del artículo a eliminar: ",self.validar_entero_positivo,"El ID debe ser un número entero positivo.")

            articulo = self.bd.obtener_articulo_por_id(int(id_articulo))
            if not articulo:
                print(f"\n{Fore.RED}No se encontró ningún artículo con ID {id_articulo}.")
                return

            print(f"\n{Fore.CYAN}Datos del artículo a eliminar:")
            datos_tabla = self.formatear_articulos_para_tabla([articulo])
            headers = ["ID", "Nombre", "Categoría", "Cantidad", "Precio Unit.", "Total"]
            print(tabulate(datos_tabla, headers=headers, tablefmt="fancy_grid"))

            confirmar = self.obtener_entrada_usuario(f"{Fore.RED}¿Está seguro de eliminar este artículo? (s/n): ",lambda x: x.lower() in ["s", "n"],"Por favor, responda 's' para sí o 'n' para no.")

            if confirmar.lower() == "s":
                exito = self.bd.eliminar_articulo(int(id_articulo))
                if exito:
                    print(f"\n{Fore.GREEN}✅ Artículo con ID {id_articulo} eliminado exitosamente.")
                else:
                    print(f"\n{Fore.RED}❌ Error al eliminar el artículo con ID {id_articulo}.")
            else:
                print(f"\n{Fore.YELLOW}Operación cancelada.")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error durante la eliminación: {e}")

    def listar_todos_articulos(self):
        """Lista todos los artículos registrados"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- LISTA DE TODOS LOS ARTÍCULOS ---")

        try:
            articulos = self.bd.obtener_todos_articulos()

            if not articulos:
                print(f"\n{Fore.YELLOW}No hay artículos registrados en el sistema.")
                return

            datos_tabla = self.formatear_articulos_para_tabla(articulos)
            headers = ["ID", "Nombre", "Categoría", "Cantidad", "Precio Unit.", "Total"]
            print(tabulate(datos_tabla, headers=headers, tablefmt="fancy_grid"))

            # Calcular y mostrar el total del presupuesto
            total_presupuesto = sum(articulo[3] * articulo[4] for articulo in articulos)
            print(f"\n{Fore.GREEN}{Style.BRIGHT}TOTAL PRESUPUESTO: ${total_presupuesto:.2f}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error al listar los artículos: {e}")

    def exportar_articulos_csv(self):
        """Exporta los artículos a un archivo CSV"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- EXPORTAR ARTÍCULOS A CSV ---")

        try:
            articulos = self.bd.obtener_todos_articulos()

            if not articulos:
                print(f"\n{Fore.YELLOW}No hay artículos para exportar.")
                return

            nombre_archivo = self.obtener_entrada_usuario("Nombre del archivo (sin extensión): ", self.validar_no_vacio,
                                                          "El nombre del archivo no puede estar vacío.")
            ruta_archivo = f"{nombre_archivo}.csv"

            # Confirmar sobrescritura si el archivo ya existe
            if os.path.exists(ruta_archivo):
                confirmar = self.obtener_entrada_usuario(
                    f"{Fore.YELLOW}El archivo ya existe. ¿Desea sobrescribirlo? (s/n): ",
                    lambda x: x.lower() in ["s", "n"],
                    "Por favor, responda 's' para sí o 'n' para no.")
                if confirmar.lower() != "s":
                    print(f"\n{Fore.YELLOW}Exportación cancelada.")
                    return

            with open(ruta_archivo, 'w', newline='', encoding='utf-8') as archivo_csv:
                escritor_csv = csv.writer(archivo_csv)

                # Escribir encabezados
                escritor_csv.writerow(
                    ['ID', 'Nombre', 'Categoría', 'Cantidad', 'Precio Unitario', 'Total', 'Descripción'])

                # Escribir datos
                for articulo in articulos:
                    id_articulo, nombre, categoria, cantidad, precio_unitario, descripcion = articulo[0:6]
                    total = cantidad * precio_unitario
                    escritor_csv.writerow([
                        id_articulo,
                        nombre,
                        categoria,
                        cantidad,
                        precio_unitario,
                        total,
                        descripcion or ""
                    ])

            print(f"\n{Fore.GREEN}✅ Artículos exportados exitosamente a '{ruta_archivo}'")

            # Preguntar si desea abrir el archivo
            abrir = self.obtener_entrada_usuario("¿Desea abrir el archivo exportado? (s/n): ",
                                                 lambda x: x.lower() in ["s", "n"],
                                                 "Por favor, responda 's' para sí o 'n' para no.")
            if abrir.lower() == "s":
                try:
                    os.startfile(ruta_archivo)  # Para Windows
                except:
                    print(f"{Fore.YELLOW}No se pudo abrir el archivo automáticamente.")
                    print(f"El archivo se encuentra en: {os.path.abspath(ruta_archivo)}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error durante la exportación: {e}")

    def registrar_gasto(self):
        """Registra un nuevo gasto con categoría"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- REGISTRAR GASTO ---")
        try:
            descripcion = self.obtener_entrada_usuario("Descripción del gasto: ", self.validar_no_vacio,
                                                       "La descripción no puede estar vacía.")
            monto = float(self.obtener_entrada_usuario("Monto del gasto: $", self.validar_numero_positivo,
                                                       "El monto debe ser un número positivo."))
            categoria = self.obtener_entrada_usuario("Categoría del gasto: ", self.validar_no_vacio,
                                                     "La categoría no puede estar vacía.")
            id_gasto = self.bd.registrar_gasto(descripcion, monto, categoria)
            if id_gasto:
                print(f"\n{Fore.GREEN}✅ Gasto registrado exitosamente con ID: {id_gasto}")
            else:
                print(f"\n{Fore.RED}❌ Error al registrar el gasto. Inténtelo nuevamente.")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error durante el registro del gasto: {e}")

    def ver_gastos(self):
        """Muestra todos los gastos registrados"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- LISTA DE GASTOS ---")
        try:
            gastos = self.bd.obtener_gastos()
            if not gastos:
                print(f"\n{Fore.YELLOW}No hay gastos registrados.")
                return
            datos_tabla = [[gasto[0], gasto[1], f"${gasto[2]:.2f}", gasto[3], gasto[4]] for gasto in gastos]
            headers = ["ID", "Descripción", "Monto", "Categoría", "Fecha"]
            print(tabulate(datos_tabla, headers=headers, tablefmt="fancy_grid"))

            # Calcular y mostrar el total de gastos
            total_gastos = sum(gasto[2] for gasto in gastos)
            print(f"\n{Fore.GREEN}{Style.BRIGHT}TOTAL GASTOS: ${total_gastos:.2f}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error al listar los gastos: {e}")

    def ver_gastos_por_categoria(self):
        """Muestra los gastos filtrados por categoría"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- VER GASTOS POR CATEGORÍA ---")
        try:
            categoria = self.obtener_entrada_usuario("Ingrese la categoría: ", self.validar_no_vacio,
                                                     "La categoría no puede estar vacía.")
            gastos = self.bd.obtener_gastos_por_categoria(categoria)
            if not gastos:
                print(f"\n{Fore.YELLOW}No hay gastos registrados en la categoría '{categoria}'.")
                return
            datos_tabla = [[gasto[0], gasto[1], f"${gasto[2]:.2f}", gasto[4]] for gasto in gastos]
            headers = ["ID", "Descripción", "Monto", "Fecha"]
            print(tabulate(datos_tabla, headers=headers, tablefmt="fancy_grid"))

            # Calcular y mostrar el total de gastos en esta categoría
            total_categoria = sum(gasto[2] for gasto in gastos)
            print(f"\n{Fore.GREEN}{Style.BRIGHT}TOTAL GASTOS EN '{categoria}': ${total_categoria:.2f}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error al listar los gastos por categoría: {e}")

    def visualizar_gastos(self):
        """Visualiza los gastos a lo largo del tiempo"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- VISUALIZAR GASTOS ---")
        try:
            gastos = self.bd.obtener_gastos()
            if not gastos:
                print(f"\n{Fore.YELLOW}No hay gastos registrados para visualizar.")
                return

            # Preparar datos para el gráfico
            fechas = []
            montos = []
            categorias = {}

            for gasto in gastos:
                fecha_obj = datetime.strptime(gasto[4],
                                              '%Y-%m-%d %H:%M:%S.%f' if '.' in gasto[4] else '%Y-%m-%d %H:%M:%S')
                fechas.append(fecha_obj)
                montos.append(gasto[2])

                # Agrupar por categoría para el gráfico de pastel
                categoria = gasto[3]
                if categoria in categorias:
                    categorias[categoria] += gasto[2]
                else:
                    categorias[categoria] = gasto[2]

            # Crear figura con dos subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

            # Gráfico de línea: gastos a lo largo del tiempo
            ax1.plot(fechas, montos, marker='o', color='blue')
            ax1.set_title('Gastos a lo largo del tiempo', fontsize=14)
            ax1.set_xlabel('Fecha', fontsize=12)
            ax1.set_ylabel('Monto ($)', fontsize=12)
            ax1.grid(True)

            # Gráfico de pastel: distribución por categoría
            labels = list(categorias.keys())
            sizes = list(categorias.values())
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax2.set_title('Distribución de gastos por categoría', fontsize=14)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"\n{Fore.RED}❌ Error al visualizar los gastos: {e}")

    def generar_reporte_presupuesto(self):
        """Genera un reporte detallado del presupuesto"""
        print(f"\n{Fore.GREEN}{Style.BRIGHT}--- REPORTE DE PRESUPUESTO ---")
        try:
            # Obtener todos los artículos
            articulos = self.bd.obtener_todos_articulos()
            gastos = self.bd.obtener_gastos()

            if not articulos and not gastos:
                print(f"\n{Fore.YELLOW}No hay artículos ni gastos registrados en el sistema.")
                return

            # Calcular estadísticas generales de artículos
            total_articulos = len(articulos)
            total_presupuesto = sum(articulo[3] * articulo[4] for articulo in articulos) if articulos else 0
            precio_promedio = total_presupuesto / total_articulos if total_articulos > 0 else 0

            # Calcular estadísticas generales de gastos
            total_gastos = sum(gasto[2] for gasto in gastos) if gastos else 0
            balance = total_presupuesto - total_gastos

            # Mostrar estadísticas generales
            print(f"\n{Fore.CYAN}{Style.BRIGHT}ESTADÍSTICAS GENERALES:")
            print(f"{Fore.CYAN}Total de artículos: {total_articulos}")
            print(f"{Fore.CYAN}Presupuesto total: ${total_presupuesto:.2f}")
            if total_articulos > 0:
                print(f"{Fore.CYAN}Precio promedio por artículo: ${precio_promedio:.2f}")
            print(f"{Fore.CYAN}Total de gastos: ${total_gastos:.2f}")
            print(f"{Fore.CYAN}Balance (Presupuesto - Gastos): ${balance:.2f}")

            # Análisis de artículos por categoría
            if articulos:
                categorias_articulos = {}
                for articulo in articulos:
                    categoria = articulo[2]
                    if categoria not in categorias_articulos:
                        categorias_articulos[categoria] = []
                    categorias_articulos[categoria].append(articulo)

                print(f"\n{Fore.CYAN}{Style.BRIGHT}ANÁLISIS DE ARTÍCULOS POR CATEGORÍA:")
                datos_categoria = []
                for categoria, arts in categorias_articulos.items():
                    total_categoria = sum(art[3] * art[4] for art in arts)
                    porcentaje = (total_categoria / total_presupuesto * 100) if total_presupuesto > 0 else 0
                    datos_categoria.append([
                        categoria,
                        len(arts),
                        f"${total_categoria:.2f}",
                        f"{porcentaje:.2f}%"
                    ])

                headers_categoria = ["Categoría", "Artículos", "Total", "% del Presupuesto"]
                print(tabulate(datos_categoria, headers=headers_categoria, tablefmt="fancy_grid"))

            # Análisis de gastos por categoría
            if gastos:
                categorias_gastos = {}
                for gasto in gastos:
                    categoria = gasto[3]
                    if categoria not in categorias_gastos:
                        categorias_gastos[categoria] = []
                    categorias_gastos[categoria].append(gasto)

                print(f"\n{Fore.CYAN}{Style.BRIGHT}ANÁLISIS DE GASTOS POR CATEGORÍA:")
                datos_gastos = []
                for categoria, gsts in categorias_gastos.items():
                    total_categoria = sum(g[2] for g in gsts)
                    porcentaje = (total_categoria / total_gastos * 100) if total_gastos > 0 else 0
                    datos_gastos.append([
                        categoria,
                        len(gsts),
                        f"${total_categoria:.2f}",
                        f"{porcentaje:.2f}%"
                    ])

                headers_gastos = ["Categoría", "Gastos", "Total", "% de Gastos"]
                print(tabulate(datos_gastos, headers=headers_gastos, tablefmt="fancy_grid"))

        except Exception as e:
            print(f"\n{Fore.RED}❌ Error al generar el reporte: {e}")

    def salir_aplicacion(self):
        """Sale de la aplicación"""
        self.ejecutando = False
        self.bd.cerrar()
        print(f"\n{Fore.CYAN}¡Gracias por usar el Sistema de Gestión de Presupuesto!")

    def ejecutar(self):
        """Ejecuta el bucle principal de la aplicación"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}¡Bienvenido al Sistema de Gestión de Presupuesto!")

        while self.ejecutando:
            self.mostrar_menu()
            eleccion = self.obtener_entrada_usuario("Ingrese una opción (1-12): ",lambda x: x in self.opciones_menu.keys(),"Opción inválida. Por favor, ingrese un número del 1 al 12.")

            # Ejecuta la opción seleccionada
            self.opciones_menu[eleccion]()


if __name__ == "__main__":
    app = AplicacionPresupuesto()
    try:
        app.ejecutar()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Programa interrumpido por el usuario.")
        app.bd.cerrar()
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error inesperado: {str(e)}")
        app.bd.cerrar()