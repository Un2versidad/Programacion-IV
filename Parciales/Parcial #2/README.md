<img width="1656" height="602" alt="image" src="https://github.com/user-attachments/assets/36463146-92e2-4ba0-a1a5-70dc843ead2e" />

<div align="center">
  <h1>💉 API de Vacunación contra Sarampión en Panamá</h1>
  <p>API REST para consultar datos históricos de vacunación contra el sarampión en niños de 12 a 23 meses en Panamá (1983-2018)</p>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License">
</div>

## 📋 Descripción

Esta API proporciona acceso a datos históricos sobre la cobertura de vacunación contra el sarampión en Panamá, basados en información del Banco Mundial (SH.IMM.MEAS). Construida con **FastAPI**, ofrece endpoints para consultar datos por año o el conjunto completo de registros entre 1983 y 2018.

## 🚀 Características

- 📊 Datos históricos de vacunación (1983-2018)
- ⚡ API REST rápida y moderna con FastAPI
- 🔍 Endpoints para consulta de datos por año o completo
- ✅ Validación de datos con Pydantic
- 📖 Documentación automática con Swagger UI

## 🛠 Instalación

1. Crea un entorno virtual e instala dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install fastapi uvicorn pydantic
```

2. Ejecuta la aplicación:
```bash
uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

## 🌐 Endpoints Disponibles

| Método | Endpoint             | Descripción                              |
|--------|----------------------|------------------------------------------|
| GET    | `/`                  | Información general de la API            |
| GET    | `/vacunas`          | Lista todos los datos de vacunación      |
| GET    | `/vacunas/{anio}`   | Obtiene datos de vacunación por año      |

### Ejemplo de solicitud
```bash
curl http://127.0.0.1:8080/vacunas/2018
```

### Respuesta
```json
{
  "anio": 2018,
  "cobertura": 98.0,
  "fuente": "Banco Mundial - SH.IMM.MEAS"
}
```

## 📚 Documentación

Accede a la documentación interactiva en:
```
http://127.0.0.1:8080/docs
```
Esto abrirá la interfaz de Swagger UI con todos los detalles de los endpoints.

## 🧪 Pruebas

Para probar la API localmente:
1. Asegúrate de que el servidor esté corriendo.
2. Usa un cliente HTTP como curl, Postman o el navegador.
3. Ejemplo con curl:
```bash
curl http://127.0.0.1:8080/vacunas
```

## 📊 Estructura de Datos

Los datos se modelan usando Pydantic con el siguiente esquema:

```python
class RegistroVacunacion(BaseModel):
    anio: int
    cobertura: float
    fuente: str = "Banco Mundial - SH.IMM.MEAS"
```

## 🔧 Tecnologías Utilizadas

- **Python 3.8+**
- **FastAPI**: Framework para construir APIs rápidas
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI para desarrollo

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
