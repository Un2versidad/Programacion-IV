# Biblioteca Personal - Sistema de Gestión de Libros

Una aplicación de línea de comandos para gestionar una biblioteca personal utilizando MongoDB como base de datos.

## 📝 Descripción

Esta aplicación permite gestionar una biblioteca personal, almacenando libros como documentos en MongoDB. Proporciona una interfaz de línea de comandos colorida y amigable para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre tu colección de libros.

## ✨ Características

- Agregar nuevos libros con título, autor, género y estado de lectura
- Actualizar información de libros existentes
- Eliminar libros de la base de datos
- Ver listado completo de libros con estadísticas
- Buscar libros por título, autor, género o en todos los campos
- Interfaz colorida y animaciones visuales
- Almacenamiento en MongoDB (base de datos NoSQL)

## 🛠️ Requisitos previos

- Python 3.6 o superior
- MongoDB (local o remoto)

## 📋 Instalación

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configura MongoDB:
   - **Opción 1: MongoDB local**
     - [Instala MongoDB Community Edition](https://docs.mongodb.com/manual/administration/install-community/)
     - Inicia el servicio MongoDB:
       ```bash
       mongod --dbpath /ruta/a/datos
       ```
   
   - **Opción 2: MongoDB Atlas (en la nube)**
     - [Crea una cuenta en MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
     - Crea un cluster gratuito
     - Obtén tu cadena de conexión desde la interfaz de Atlas

3. Configura la cadena de conexión:
   - Edita el archivo `gestor_libros.py` y actualiza la URL de conexión:
     ```python
     # Para MongoDB local
     uri = "mongodb://localhost:27017"
     
     # Para MongoDB Atlas
     # uri = "mongodb+srv://usuario:contraseña@cluster.mongodb.net/"
     ```

## 🚀 Uso

Para ejecutar la aplicación:

```bash
python biblioteca.py
```

### Menú Principal

1. **Agregar un nuevo libro** - Registra un nuevo libro en la base de datos
2. **Actualizar información de libro** - Modifica cualquier campo de un libro existente
3. **Eliminar un libro** - Elimina un libro de la base de datos
4. **Listar todos los libros** - Muestra todos los libros con estadísticas
5. **Buscar libros** - Busca libros por diferentes criterios
6. **Salir** - Termina la aplicación

### Ejemplos de documentos

Estructura de un documento de libro en MongoDB:

```json
{
  "_id": "60a7c8c8c9d4b2d7c8a1b2c3",
  "titulo": "Cien años de soledad",
  "autor": "Gabriel García Márquez",
  "genero": "Realismo mágico",
  "estado_lectura": "Leído"
}
```

## 📚 Estructura del Proyecto

- `biblioteca.py` - Archivo principal de la aplicación (interfaz de usuario)
- `gestor_libros.py` - Clase para gestionar operaciones con MongoDB
- `requirements.txt` - Dependencias del proyecto

## 📦 Dependencias

- `pymongo` - Cliente de MongoDB para Python
- `bson` - Manejo de ObjectID para MongoDB
- `colorama` - Colores en terminal
- `tabulate` - Formateo de tablas
- `pyfiglet` - Textos ASCII art
- `tqdm` - Barras de progreso

## ⚠️ Resolución de problemas

### Error de conexión a MongoDB
- Verifica que el servicio de MongoDB esté ejecutándose
- Comprueba que la cadena de conexión sea correcta
- Asegúrate de tener permisos de acceso a la base de datos
- Por defecto, la aplicación usa `mongodb://admin:admin123@localhost:27017` con Docker

### Documentos no encontrados
- Verifica que estás usando la colección correcta
- Comprueba los términos de búsqueda
- Asegúrate de que la base de datos `biblioteca_personal` y la colección `libros` existan

## 👨‍💻 Autor

Tu Nombre - [tu-usuario](https://github.com/fl2on
