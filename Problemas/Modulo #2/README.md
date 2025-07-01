![image](https://github.com/user-attachments/assets/af49234c-c4df-4b60-839d-8318b115b6ae)

# 📚 Biblioteca Personal con SQLite en Python

Aplicación de línea de comandos para gestionar tu biblioteca personal, almacenando datos en una base de datos SQLite.

## 🚀 Funcionalidades

- Agregar nuevo libro (título, autor, género, estado leído/no leído)  
- Actualizar información de libros existentes  
- Eliminar libros  
- Listar todos los libros registrados  
- Buscar libros por título, autor o género  
- Salir del programa de forma controlada  

## 🛠 Requisitos

- Python 3.8+  
- Módulo `sqlite3` (incluido en Python estándar)  
- Librerías externas: `colorama`, `tabulate`

## 📦 Instalación de dependencias

Para instalar las librerías necesarias:

```bash
pip install colorama tabulate
```

## 📋 Ejecución

Ejecuta el programa con:

```bash
python main.py
```

Al iniciarse, se creará automáticamente la base de datos `biblioteca.db` y la tabla `libros` si no existen.

## 📝 Uso

Al ejecutar el programa verás un menú interactivo con las siguientes opciones:

1. Agregar nuevo libro  
2. Actualizar información de un libro  
3. Eliminar libro existente  
4. Ver listado de libros  
5. Buscar libros  
6. Salir

Sigue las indicaciones en pantalla para ingresar datos y realizar las operaciones.

## 🛡 Manejo de errores

- Validación de campos obligatorios al agregar y actualizar libros.  
- Manejo de errores en operaciones con SQLite, mostrando mensajes en caso de fallos.  
- Validación de entradas numéricas para seleccionar opciones y IDs.  

## 📸 Capturas

![image](https://github.com/user-attachments/assets/570cd5c0-daa5-44e1-ae20-727d35c2fd52)

## 🧑‍💻 Código modularizado

- Clase `Biblioteca` que gestiona toda la interacción con la base de datos SQLite.  
- Funciones para mostrar menú, validar entradas y formatear tablas para visualización clara.
