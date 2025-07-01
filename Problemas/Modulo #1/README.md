![image](https://github.com/user-attachments/assets/b3ef648c-1552-4027-aea2-2b6dad61b505)

# 🤖 Sistema de Gestión de Aventuras

## 🎯 Objetivo
Diseñar una base de datos relacional utilizando SQLite que permita registrar información clave sobre misiones, héroes participantes y monstruos enfrentados en un mundo de aventuras.

## 📝 Contexto
Un gremio de aventureros necesita un sistema para registrar:

- Las **misiones realizadas** (ubicación, dificultad y recompensa).
- Los **héroes participantes** (clase, nivel de experiencia, múltiples misiones).
- Los **monstruos enfrentados** en cada misión.

Este proyecto implementa una base de datos relacional que cumple con los requisitos mencionados, utilizando SQLite como motor de base de datos.

## 📌 Requisitos del modelo

### 🔹 Entidades principales

#### 1. Héroes
- **Nombre**: Nombre del héroe.
- **Clase**: Tipo de héroe (Guerrero, Mago, Arquero, Clérigo, Ladrón).
- **Nivel de experiencia**: Valor numérico positivo que indica la habilidad del héroe.

#### 2. Misiones
- **Nombre o descripción**: Breve descripción de la misión.
- **Nivel de dificultad**: Valor entre 1 y 10 que indica la complejidad de la misión.
- **Localización**: Lugar donde se realiza la misión.
- **Recompensa**: Cantidad de monedas de oro otorgadas por completar la misión.

#### 3. Monstruos
- **Nombre**: Nombre del monstruo.
- **Tipo**: Categoría del monstruo (Dragón, Goblin, No-muerto, etc.).
- **Nivel de amenaza**: Valor entre 1 y 10 que indica la peligrosidad del monstruo.

### 🔹 Relaciones

1. **Héroes y Misiones**:
   - Un héroe puede participar en muchas misiones.
   - Una misión puede tener muchos héroes.
   - Relación: **muchos-a-muchos**.

2. **Misiones y Monstruos**:
   - Una misión puede tener muchos monstruos.
   - Un monstruo puede aparecer en varias misiones.
   - Relación: **muchos-a-muchos**.

## 🛠️ Entregables

### Modelo lógico
A continuación se describe el modelo lógico de la base de datos:

#### Tabla: `heroes`
- **id** (`INTEGER`, `PRIMARY KEY`): Identificador único del héroe.
- **nombre** (`TEXT`): Nombre del héroe.
- **clase** (`TEXT`): Clase del héroe (Guerrero, Mago, Arquero, Clérigo, Ladrón). Validado mediante `CHECK`.
- **nivel_experiencia** (`INTEGER`): Nivel de experiencia del héroe. Debe ser mayor a 0.

#### Tabla: `misiones`
- **id** (`INTEGER`, `PRIMARY KEY`): Identificador único de la misión.
- **nombre** (`TEXT`): Nombre o descripción de la misión.
- **nivel_dificultad** (`INTEGER`): Nivel de dificultad de la misión (entre 1 y 10). Validado mediante `CHECK`.
- **localizacion** (`TEXT`): Localización de la misión.
- **recompensa** (`INTEGER`): Recompensa en monedas de oro. Debe ser mayor o igual a 0.

#### Tabla: `monstruos`
- **id** (`INTEGER`, `PRIMARY KEY`): Identificador único del monstruo.
- **nombre** (`TEXT`): Nombre del monstruo.
- **tipo** (`TEXT`): Tipo de monstruo (Dragón, Goblin, No-muerto, etc.).
- **nivel_amenaza** (`INTEGER`): Nivel de amenaza del monstruo (entre 1 y 10). Validado mediante `CHECK`.

#### Tabla: `misiones_heroes`
- **id** (`INTEGER`, `PRIMARY KEY`): Identificador único de la relación.
- **mision_id** (`INTEGER`): ID de la misión asociada. Referencia a la tabla `misiones`.
- **heroe_id** (`INTEGER`): ID del héroe asociado. Referencia a la tabla `heroes`.
- **UNIQUE(mision_id, heroe_id)**: Garantiza que no haya duplicados en las relaciones.

#### Tabla: `misiones_monstruos`
- **id** (`INTEGER`, `PRIMARY KEY`): Identificador único de la relación.
- **mision_id** (`INTEGER`): ID de la misión asociada. Referencia a la tabla `misiones`.
- **monstruo_id** (`INTEGER`): ID del monstruo asociado. Referencia a la tabla `monstruos`.
- **UNIQUE(mision_id, monstruo_id)**: Garantiza que no haya duplicados en las relaciones.

### Modelo entidad-relación (ER)
El modelo ER incluye las siguientes entidades y relaciones:

1. **Entidades principales**:
   - `heroes`
   - `misiones`
   - `monstruos`

2. **Relaciones**:
   - `misiones_heroes`: Conecta `misiones` con `heroes`.
   - `misiones_monstruos`: Conecta `misiones` con `monstruos`.

## 💡 Consideraciones técnicas

1. **Claves primarias y foráneas**:
   - Todas las tablas tienen claves primarias (`id`) para identificar registros únicos.
   - Las tablas puente (`misiones_heroes` y `misiones_monstruos`) utilizan claves foráneas para relacionar las entidades principales.

2. **Restricciones**:
   - Se utilizan restricciones `CHECK` para validar valores específicos, como el nivel de dificultad, el nivel de amenaza y la clase de los héroes.

3. **Datos de prueba**:
   - La función `insertar_datos_ficticios` inserta datos de ejemplo en las tablas para facilitar la verificación del funcionamiento del sistema.

4. **Eliminación previa de la base de datos**:
   - Antes de crear la base de datos, se verifica si existe un archivo previo y se elimina para evitar conflictos.

## 📂 Estructura esperada del modelo lógico

| Tabla              | Descripción                                      |
|--------------------|--------------------------------------------------|
| `heroes`           | Información de cada héroe                       |
| `misiones`         | Detalles de cada misión                         |
| `monstruos`        | Información de cada monstruo                    |
| `misiones_heroes`  | Relación entre misiones y héroes (participación) |
| `misiones_monstruos` | Relación entre misiones y monstruos (enemigos enfrentados) |

## 🚀 Ejecución del proyecto

1. **Requisitos**:
   - Python 3.x instalado en tu sistema.
   - Librería `sqlite3` (incluida en la biblioteca estándar de Python).

2. **Pasos para ejecutar**:
   - Guarda el script Python en un archivo, `gremio.py`.
   - Ejecuta el script desde la terminal:
     ```bash
     python gremio.py
     ```
   - El script creará un archivo llamado `aventuras.db` en el mismo directorio y lo llenará con datos de prueba.

3. **Verificación**:
   - Puedes usar herramientas como [DB Browser for SQLite](https://sqlitebrowser.org/) para explorar el contenido de la base de datos generada.
