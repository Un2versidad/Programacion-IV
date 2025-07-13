
<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <h1>💸 Sistema de Gestión de Presupuesto</h1>
  <p>Un sistema interactivo para gestionar artículos y gastos con SQLite, visualización de datos y exportación a CSV.</p>
</div>

---

## 📋 Descripción

**Sistema de Gestión de Presupuesto** es una aplicación de consola desarrollada en Python que permite administrar un presupuesto personal o empresarial. Utiliza una base de datos SQLite para almacenar artículos y gastos, ofrece una interfaz interactiva con menús coloreados, y proporciona herramientas para buscar, editar, eliminar y visualizar datos financieros.

### ✨ Características Principales

- **Gestión de Artículos**: Registra, edita, elimina y busca artículos por nombre o categoría.
- **Gestión de Gastos**: Registra gastos con categorías y fechas, y filtra por categoría.
- **Visualización de Datos**: Genera gráficos de línea (gastos a lo largo del tiempo) y de pastel (distribución por categoría) con Matplotlib.
- **Exportación a CSV**: Exporta artículos a archivos CSV con opción de apertura automática.
- **Reportes Detallados**: Genera reportes con estadísticas de presupuesto, gastos y análisis por categoría.
- **Interfaz Amigable**: Menús coloreados con Colorama y tablas formateadas con Tabulate.
- **Validación Robusta**: Entradas validadas para evitar errores de usuario.
- **Manejo de Errores**: Gestión completa de excepciones con mensajes claros.

---

## 🚀 Instalación

Sigue estos pasos para instalar y ejecutar el sistema en tu máquina.

### Prerrequisitos

- Python 3.8 o superior
- Sistema operativo: Windows, macOS o Linux
- Dependencias:
  - `sqlite3` (incluido en Python)
  - `colorama`
  - `tabulate`
  - `matplotlib`

### Pasos de Instalación

1. **Crea un Entorno Virtual** (opcional, pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. **Instala las Dependencias**:
   ```bash
   pip install colorama tabulate matplotlib
   ```

3. **Ejecuta la Aplicación**:
   ```bash
   python main.py
   ```

---

## 🛠️ Uso

1. **Iniciar la Aplicación**:
   - Ejecuta `python app.py` para iniciar el sistema.
   - Verás un mensaje de bienvenida y el menú principal.

2. **Menú Principal**:
   <div align="center">
     <img src="https://via.placeholder.com/600x200?text=Men%C3%BA+Principal" alt="Menú Principal">
   </div>
   - Selecciona una opción (1-12) ingresando el número correspondiente.
   - Las opciones incluyen:
     - **1**: Registrar un nuevo artículo (nombre, categoría, cantidad, precio, descripción).
     - **2**: Buscar artículos por nombre o categoría.
     - **3**: Editar un artículo existente.
     - **4**: Eliminar un artículo.
     - **5**: Listar todos los artículos.
     - **6**: Exportar artículos a CSV.
     - **7**: Registrar un gasto.
     - **8**: Ver todos los gastos.
     - **9**: Ver gastos por categoría.
     - **10**: Visualizar gráficos de gastos.
     - **11**: Generar reporte detallado.
     - **12**: Salir.

3. **Ejemplo de Interacción**:
   - **Registrar un Artículo**:
     ```
     Nombre del artículo: Laptop
     Categoría: Electrónica
     Cantidad: 1
     Precio unitario: $1000
     Descripción (opcional): Laptop nueva
     ✅ Artículo registrado exitosamente con ID: 1
     ```
   - **Visualizar Gastos**:
     - Genera gráficos de línea y pastel mostrando la evolución y distribución de los gastos.

---

## 📊 Ejemplo de Salida

### Tabla de Artículos
```
╒══════╤══════════╤══════════════╤═══════════╤═══════════════╤══════════╕
│ ID   │ Nombre   │ Categoría    │ Cantidad  │ Precio Unit.  │ Total    │
╞══════╪══════════╪══════════════╪═══════════╪═══════════════╪══════════╡
│ 1    │ Laptop   │ Electrónica  │ 1.00      │ $1,000.00     │ $1,000.00│
│ 2    │ Silla    │ Muebles      │ 2.00      │ $50.00        │ $100.00  │
╘══════╧══════════╧══════════════╧═══════════╧═══════════════╧══════════╛
TOTAL PRESUPUESTO: $1,100.00
```

### Gráficos de Gastos
<div align="center">
  <img src="https://via.placeholder.com/600x300?text=Gr%C3%A1fico+de+Gastos" alt="Gráficos de Gastos">
</div>

---

## 🗄️ Estructura del Proyecto

```plaintext
sistema-gestion-presupuesto/
├── app.py                # Código principal del sistema
├── presupuesto.db         # Base de datos SQLite (generada al ejecutar)
├── README.md              # Este archivo
└── requirements.txt       # Lista de dependencias
```

---

## 🔧 Tecnologías Utilizadas

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Matplotlib-11557C?logo=python&logoColor=white" alt="Matplotlib">
</div>

- **Python**: Lenguaje principal para la lógica de la aplicación.
- **SQLite**: Base de datos ligera para almacenar artículos y gastos.
- **Matplotlib**: Generación de gráficos de visualización.
- **Colorama**: Estilización de la consola con colores.
- **Tabulate**: Formateo de tablas en la consola.

---

## 📝 Requisitos de la Base de Datos

La aplicación crea automáticamente un archivo `presupuesto.db` con dos tablas:

- **articulos**:
  - `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  - `nombre` (TEXT, NOT NULL)
  - `categoria` (TEXT, NOT NULL)
  - `cantidad` (REAL, NOT NULL)
  - `precio_unitario` (REAL, NOT NULL)
  - `descripcion` (TEXT)
  - `creado_en` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
  - `actualizado_en` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

- **gastos**:
  - `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  - `descripcion` (TEXT, NOT NULL)
  - `monto` (REAL, NOT NULL)
  - `categoria` (TEXT, NOT NULL)
  - `fecha` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

---

## 🐛 Manejo de Errores

- **Errores de Base de Datos**: Capturados y mostrados en rojo con mensajes claros.
- **Validación de Entrada**: Asegura que los datos ingresados sean válidos (no vacíos, números positivos, etc.).
- **Interrupción del Programa**: Maneja `KeyboardInterrupt` para una salida limpia.

---

## 📜 Licencia

Este proyecto está licenciado bajo la [Licencia MIT](https://github.com/Un2versidad/Programacion-IV/blob/main/LICENSE).
