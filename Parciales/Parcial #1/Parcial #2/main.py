# Importaciones necesarias
from typing import List  # Para tipar listas
from fastapi import FastAPI, HTTPException, Path  # Framework web, manejo de errores y validación de path
from pydantic import BaseModel  # Para definir modelos de datos
import uvicorn  # Servidor ASGI para ejecutar la aplicación

# --------------------- MODELOS ---------------------
class RegistroVacunacion(BaseModel):
    """
    Modelo de datos para representar un registro de vacunación.

    Attributes:
        anio: Año del registro de vacunación
        cobertura: Porcentaje de cobertura de vacunación
        fuente: Origen de los datos, por defecto "Banco Mundial - SH.IMM.MEAS"
    """
    anio: int
    cobertura: float
    fuente: str = "Banco Mundial - SH.IMM.MEAS"

# --------------------- DATOS ---------------------
# Diccionario con datos históricos de vacunación contra sarampión en Panamá
# Clave: año (1983-2018), Valor: porcentaje de cobertura
datos_vacunacion = {
    1983: 85.0, 1984: 72.0, 1985: 85.0, 1986: 74.0, 1987: 78.0,
    1988: 73.0, 1989: 73.0, 1990: 73.0, 1991: 80.0, 1992: 76.0,
    1993: 83.0, 1994: 84.0, 1995: 84.0, 1996: 90.0, 1997: 92.0,
    1998: 96.0, 1999: 90.0, 2000: 97.0, 2001: 95.0, 2002: 95.0,
    2003: 95.0, 2004: 97.0, 2005: 99.0, 2006: 95.0, 2007: 95.0,
    2008: 96.0, 2009: 96.0, 2010: 97.0, 2011: 97.0, 2012: 98.0,
    2013: 92.0, 2014: 90.0, 2015: 93.0, 2016: 95.0, 2017: 98.0,
    2018: 98.0
}

# --------------------- API ---------------------
# Inicialización de la aplicación FastAPI con metadatos
app = FastAPI(
    title="API de Vacunación contra Sarampión en Panamá",
    description="Datos históricos sobre la vacunación contra el sarampión en niños de 12 a 23 meses en Panamá",
    version="1.0.0"
)

@app.get("/", tags=["Información"])
async def raiz():
    """
    Endpoint raíz que proporciona información general sobre la API.

    Returns: dict: Mensaje informativo y lista de endpoints disponibles
    """
    return {
        "mensaje": "API de datos históricos de vacunación contra sarampión en Panamá",
        "endpoints_disponibles": [
            "/vacunas",
            "/vacunas/{anio}"
        ]
    }

@app.get("/vacunas", response_model=List[RegistroVacunacion], tags=["Vacunas"])
async def obtener_todos_datos_vacunacion():
    """
    Obtiene todos los registros de vacunación disponibles.

    Returns: List[RegistroVacunacion]: Lista ordenada cronológicamente de todos los registros
    """
    return sorted([
        RegistroVacunacion(anio=anio, cobertura=cobertura)
        for anio, cobertura in datos_vacunacion.items()
    ], key=lambda x: x.anio)

@app.get("/vacunas/{anio}", response_model=RegistroVacunacion, tags=["Vacunas"])
async def obtener_vacunacion_por_anio(anio: int = Path(..., ge=1983, le=2018, description="Año entre 1983 y 2018")):
    """
    Obtiene el registro de vacunación para un año específico.

    Args: anio: Año del que se desea obtener la información (entre 1983 y 2018)

    Returns: RegistroVacunacion: Datos de vacunación para el año solicitado

    Raises: HTTPException: Si no existen datos para el año solicitado
    """
    if anio not in datos_vacunacion:
        raise HTTPException(status_code=404, detail=f"No hay datos disponibles para el año {anio}")
    return RegistroVacunacion(anio=anio, cobertura=datos_vacunacion[anio])

if __name__ == "__main__":
    """
    Punto de entrada para ejecutar la aplicación directamente.
    Configura el servidor uvicorn para servir la API en http://127.0.0.1:8080
    con recarga automática activada para facilitar el desarrollo.
    """
    import os

    nombre_modulo = os.path.splitext(os.path.basename(__file__))[0]
    uvicorn.run(f"{nombre_modulo}:app", host="127.0.0.1", port=8080, reload=True)