import os
import time
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_restful import Api, Resource
import requests
from dotenv import load_dotenv
import threading

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración de la API
URL_BASE_API = os.getenv("URL_BASE_API", "http://localhost:5000/api")

directorio_base = os.path.abspath(os.path.dirname(__file__))
directorio_plantillas = os.path.join(directorio_base, 'templates')

# Variable para controlar si la API está lista
api_lista = threading.Event()

# --------------------------------
# Implementación de la API (Backend)
# --------------------------------
app_api = Flask(__name__, template_folder=directorio_plantillas)
app_api.config['TEMPLATES_AUTO_RELOAD'] = True
api = Api(app_api, prefix='/api')

# Base de datos en memoria para demostración
bd_libros = [
    {"id": 1, "titulo": "Don Quijote", "autor": "Miguel de Cervantes", "año": 1605},
    {"id": 2, "titulo": "Cien años de soledad", "autor": "Gabriel García Márquez", "año": 1967},
    {"id": 3, "titulo": "Rayuela", "autor": "Julio Cortázar", "año": 1963}
]
siguiente_id = 4

# Mutex para proteger accesos a bd_libros
bd_mutex = threading.Lock()

class RecursoLibro(Resource):
    def get(self, id_libro=None):
        with bd_mutex:
            if id_libro is None:
                return jsonify(bd_libros)

            libro = next((l for l in bd_libros if l["id"] == id_libro), None)
            if libro:
                return jsonify(libro)
            return {"error": "Libro no encontrado"}, 404

    def post(self):
        global siguiente_id
        datos = request.get_json()

        if not all(campo in datos for campo in ["titulo", "autor", "año"]):
            return {"error": "Faltan campos requeridos"}, 400

        with bd_mutex:
            nuevo_libro = {
                "id": siguiente_id,
                "titulo": datos["titulo"],
                "autor": datos["autor"],
                "año": datos["año"]
            }
            bd_libros.append(nuevo_libro)
            siguiente_id += 1

            return jsonify(nuevo_libro), 201

    def put(self, id_libro):
        datos = request.get_json()

        with bd_mutex:
            libro = next((l for l in bd_libros if l["id"] == id_libro), None)
            if not libro:
                return {"error": "Libro no encontrado"}, 404

            if "titulo" in datos:
                libro["titulo"] = datos["titulo"]
            if "autor" in datos:
                libro["autor"] = datos["autor"]
            if "año" in datos:
                libro["año"] = datos["año"]

            return jsonify(libro)

    def delete(self, id_libro):
        global bd_libros

        with bd_mutex:
            libro = next((l for l in bd_libros if l["id"] == id_libro), None)
            if not libro:
                return {"error": "Libro no encontrado"}, 404

            bd_libros = [l for l in bd_libros if l["id"] != id_libro]
            return {"mensaje": "Libro eliminado correctamente"}, 200

# Registrar recursos con la API
api.add_resource(RecursoLibro, '/books', '/books/<int:id_libro>', endpoint='libros')

# Añadir ruta para el endpoint raíz de la API
@app_api.route('/api')
def raiz_api():
    return jsonify({
        "mensaje": "Biblioteca API",
        "endpoints": {
            "GET /api/books": "Listar todos los libros",
            "GET /api/books/<id>": "Obtener un libro específico",
            "POST /api/books": "Crear un nuevo libro",
            "PUT /api/books/<id>": "Actualizar un libro",
            "DELETE /api/books/<id>": "Eliminar un libro"
        }
    })


# --------------------------------
# Implementación del Cliente (Aplicación Web Flask)
# --------------------------------

app_cliente = Flask(__name__, template_folder=directorio_plantillas)
app_cliente.config['TEMPLATES_AUTO_RELOAD'] = True
app_cliente.secret_key = os.getenv("CLAVE_SECRETA", "clave-desarrollo")

# Caché local para datos críticos
cache_libros = None
cache_timestamp = 0
CACHE_VALIDEZ = 30  # segundos

def obtener_libro_cache(id_libro):
    """Intenta obtener un libro desde la caché local"""
    global cache_libros
    if cache_libros and time.time() - cache_timestamp < CACHE_VALIDEZ:
        libro = next((l for l in cache_libros if l["id"] == id_libro), None)
        if libro:
            logger.info(f"Libro {id_libro} encontrado en caché")
            return libro
    return None


def actualizar_cache():
    """Actualiza la caché de libros"""
    global cache_libros, cache_timestamp
    try:
        respuesta = requests.get(f"{URL_BASE_API}/books", timeout=2)
        if respuesta.status_code == 200:
            cache_libros = respuesta.json()
            cache_timestamp = time.time()
            logger.info("Caché de libros actualizada")
            return True
        return False
    except:
        return False


# Función para realizar solicitudes HTTP con reintentos
def hacer_solicitud(metodo, url, max_intentos=5, **kwargs):
    tiempo_espera = 0.5

    # Intentar actualizar la caché primero
    if metodo.lower() == 'get' and '/books' in url and not '/books/' in url:
        actualizar_cache()

    # Esperar a que la API esté lista
    if not api_lista.is_set():
        logger.warning("Esperando a que la API esté lista...")
        for _ in range(10):  # Máximo 5 segundos de espera
            try:
                requests.get(f"{URL_BASE_API}", timeout=0.5)
                api_lista.set()
                logger.info("API detectada y lista")
                break
            except:
                time.sleep(0.5)

    for intento in range(max_intentos):
        try:
            logger.info(f"Intento {intento + 1} para {metodo} {url}")
            respuesta = requests.request(
                method=metodo,
                url=url,
                timeout=5,
                **kwargs
            )
            # Registrar la respuesta para depuración
            logger.info(f"Respuesta: {respuesta.status_code}")
            if respuesta.status_code >= 400:
                logger.warning(f"Error {respuesta.status_code}: {respuesta.text}")

            return respuesta
        except requests.RequestException as e:
            logger.error(f"Error en solicitud ({intento + 1}/{max_intentos}): {str(e)}")
            if intento == max_intentos - 1:
                raise
            time.sleep(tiempo_espera)
            tiempo_espera = min(tiempo_espera * 2, 5)  # Espera exponencial con límite de 5 segundos
@app_cliente.route('/')
def inicio():
    global cache_libros, cache_timestamp  # Mover al inicio de la función

    try:
        # Intenta usar la caché primero
        if cache_libros and time.time() - cache_timestamp < CACHE_VALIDEZ:
            logger.info("Usando caché para mostrar libros")
            return render_template('index.html', libros=cache_libros)

        # Si no hay caché válida, consulta la API
        respuesta = hacer_solicitud('get', f"{URL_BASE_API}/books")

        if respuesta.status_code == 200:
            libros = respuesta.json()
            # Actualizar caché
            cache_libros = libros
            cache_timestamp = time.time()
            return render_template('index.html', libros=libros)
        else:
            flash(f"Error al obtener libros: {respuesta.status_code}", "error")
            # Intentar usar caché antigua como fallback
            if cache_libros:
                flash("Mostrando datos almacenados en caché", "warning")
                return render_template('index.html', libros=cache_libros)
            return render_template('index.html', libros=[])
    except requests.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        # Intentar usar caché antigua como fallback
        if cache_libros:
            flash("Mostrando datos almacenados en caché", "warning")
            return render_template('index.html', libros=cache_libros)
        return render_template('index.html', libros=[])

@app_cliente.route('/libro/<int:id_libro>')
def ver_libro(id_libro):
    # Intentar obtener de caché primero
    libro_cache = obtener_libro_cache(id_libro)
    if libro_cache:
        return render_template('detalle_libro.html', libro=libro_cache)

    try:
        respuesta = hacer_solicitud('get', f"{URL_BASE_API}/books/{id_libro}")

        if respuesta.status_code == 200:
            libro = respuesta.json()
            return render_template('detalle_libro.html', libro=libro)
        else:
            flash("Libro no encontrado", "error")
            return redirect(url_for('inicio'))
    except requests.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        if libro_cache:  # Si falló pero tenemos caché
            flash("Mostrando datos almacenados en caché", "warning")
            return render_template('detalle_libro.html', libro=libro_cache)
        return redirect(url_for('inicio'))

@app_cliente.route('/libro/nuevo', methods=['GET', 'POST'])
def agregar_libro():
    if request.method == 'POST':
        try:
            datos_libro = {
                "titulo": request.form.get('titulo'),
                "autor": request.form.get('autor'),
                "año": int(request.form.get('año'))
            }

            respuesta = hacer_solicitud(
                'post',
                f"{URL_BASE_API}/books",
                json=datos_libro
            )

            if respuesta.status_code == 201:
                flash("¡Libro agregado correctamente!", "success")
                return redirect(url_for('inicio'))
            else:
                mensaje_error = respuesta.json().get('error', 'Error desconocido')
                flash(f"Error al agregar libro: {mensaje_error}", "error")
        except requests.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
        except ValueError:
            flash("Valor de año inválido", "error")

    return render_template('formulario_libro.html', libro=None, accion="Agregar")

@app_cliente.route('/libro/editar/<int:id_libro>', methods=['GET', 'POST'])
def editar_libro(id_libro):
    if request.method == 'POST':
        try:
            datos_libro = {
                "titulo": request.form.get('titulo'),
                "autor": request.form.get('autor'),
                "año": int(request.form.get('año'))
            }

            respuesta = hacer_solicitud(
                'put',
                f"{URL_BASE_API}/books/{id_libro}",
                json=datos_libro
            )

            if respuesta.status_code == 200:
                flash("¡Libro actualizado correctamente!", "success")
                return redirect(url_for('inicio'))
            else:
                mensaje_error = respuesta.json().get('error', 'Error desconocido')
                flash(f"Error al actualizar libro: {mensaje_error}", "error")
        except requests.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
        except ValueError:
            flash("Valor de año inválido", "error")
    else:
        try:
            respuesta = hacer_solicitud('get', f"{URL_BASE_API}/books/{id_libro}")

            if respuesta.status_code == 200:
                libro = respuesta.json()
                return render_template('formulario_libro.html', libro=libro, accion="Editar")
            else:
                flash("Libro no encontrado", "error")
                return redirect(url_for('inicio'))
        except requests.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
            return redirect(url_for('inicio'))

@app_cliente.route('/libro/eliminar/<int:id_libro>', methods=['POST'])
def eliminar_libro(id_libro):
    try:
        respuesta = hacer_solicitud('delete', f"{URL_BASE_API}/books/{id_libro}")

        if respuesta.status_code == 200:
            flash("¡Libro eliminado correctamente!", "success")
        else:
            mensaje_error = respuesta.json().get('error', 'Error desconocido')
            flash(f"Error al eliminar libro: {mensaje_error}", "error")
    except requests.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")

    return redirect(url_for('inicio'))

# Inicialización y arranque
if __name__ == "__main__":
    # Recomendación importante
    print("=" * 80)
    print("RECOMENDACIÓN IMPORTANTE")
    print("Esta configuración de ejecución dual (API + cliente) en el mismo proceso")
    print("es solo para fines de desarrollo y puede causar problemas.")
    print("Para un entorno de producción, ejecute la API y el cliente como procesos separados:")
    print("\n1. En una terminal: python api.py")
    print("2. En otra terminal: python cliente.py")
    print("=" * 80)

    time.sleep(3)  # Dar tiempo para leer el mensaje

    # Iniciar hilo de la API
    def ejecutar_api():
        logger.info("Iniciando servidor API en puerto 5000")
        app_api.run(host='0.0.0.0', port=5000, threaded=True)


    hilo_api = threading.Thread(target=ejecutar_api)
    hilo_api.daemon = True
    hilo_api.start()

    # Esperar a que la API esté lista
    logger.info("Esperando a que la API inicie...")
    time.sleep(5)  # Dar más tiempo para que la API inicie

    # Verificar API
    try:
        requests.get(f"{URL_BASE_API}", timeout=2)
        api_lista.set()
        logger.info("API verificada y funcionando")
    except requests.RequestException:
        logger.warning("No se pudo verificar la API, pero continuando de todos modos")

    # Pre-cargar caché
    actualizar_cache()

    # Ejecutar cliente
    logger.info("Iniciando servidor cliente en puerto 5001")
    app_cliente.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)