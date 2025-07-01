![image](https://github.com/user-attachments/assets/080b279a-5a8b-45a9-b7ca-0a4d1c445dcd)

# 📚 Biblioteca Personal con MariaDB y SQLAlchemy

¡Bienvenido a tu aplicación de biblioteca personal en Python!  
Esta versión utiliza **MariaDB** como sistema de base de datos y **SQLAlchemy** como ORM para un manejo moderno, robusto y portable.

## 🚀 Características

✔️ Agregar libros (título, autor, género, estado de lectura)  
✔️ Ver todos los libros registrados  
✔️ Buscar libros por título, autor o género  
✔️ Actualizar información de un libro existente  
✔️ Eliminar un libro  
✔️ Salida controlada y segura

## 📸 Screenshot

![image](https://github.com/user-attachments/assets/c8558852-4dbe-4f0c-96fa-5d3601cfd055)

## 🛠️ Requisitos

- Python 3.8 o superior  
- MariaDB Server  
- pip

## ⚙️ Instalación de dependencias

1️⃣ Instala las dependencias de Python:

```bash
pip install -r requirements.txt
```

## 🐬 Instalación de MariaDB

### 💻 En Windows

- Descarga el instalador desde https://mariadb.org/download/  
- Sigue el asistente e instala el servidor  
- Anota el usuario, contraseña y puerto

### 🐧 En Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install mariadb-server
```

- Inicia el servicio:

```bash
sudo systemctl start mariadb
```

- (Opcional) Configura el usuario root:

```bash
sudo mysql_secure_installation
```

## 🗄️ Creación de la base de datos

⚡ ¡La app creará la base de datos automáticamente si no existe!

Pero si quieres hacerlo manualmente:

```sql
CREATE DATABASE biblioteca;
```

## 📝 Configuración de conexión

El primer arranque de la app generará un archivo:

```
db_config.ini
```

Contenido ejemplo:

```
[Database]
user = root
password = admin123
host = localhost
database = biblioteca
```

✅ Edita este archivo con tus credenciales reales antes de iniciar.

## 🏃‍♂️ Ejecutar la aplicación

```bash
python main.py
```

✅ La app se conectará a MariaDB, creará la base de datos y tablas si no existen y te mostrará el menú interactivo.

## 🔄 Flujo de uso

1️⃣ Selecciona una opción del menú:  
- 1. Agregar nuevo libro  
- 2. Ver todos los libros  
- 3. Buscar libros  
- 4. Actualizar información  
- 5. Eliminar libro  
- 6. Salir

2️⃣ Ingresa los datos solicitados en consola.

3️⃣ ¡Disfruta tu biblioteca personal gestionada con MariaDB!

---

## ❤️ Créditos

- SQLAlchemy ORM  
- MariaDB  
- Colorama y Tabulate para consola  
