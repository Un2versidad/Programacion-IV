from flask import Flask, render_template, request, redirect, url_for, flash
import redis
import uuid
import os
from dotenv import load_dotenv
from flask_mail import Mail, Message
from celery_app import make_celery

# Cargar variables de entorno
load_dotenv()

# Inicializar aplicación Flask
app = Flask(__name__)
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT')),
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS') == 'True',
    CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
    CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)
# Inicializar Flask-Mail
mail = Mail(app)

# Inicializar Celery
celery = make_celery(app)

app.secret_key = os.getenv('SECRET_KEY', 'clave_desarrollo')

# Clase para simular Redis cuando no está disponible
class MockRedis:
    def __init__(self):
        self.data = {}
        print("⚠️ Usando base de datos en memoria (MockRedis)")

    def keys(self, pattern):
        prefix = pattern.replace('*', '')
        return [k for k in self.data.keys() if k.startswith(prefix)]

    def type(self, key):
        return 'hash' if key in self.data else 'none'

    def hgetall(self, key):
        return self.data.get(key, {})

    def hset(self, key, mapping=None, **kwargs):
        if key not in self.data:
            self.data[key] = {}
        self.data[key].update(mapping or kwargs)
        return len(mapping or kwargs)

    def exists(self, key):
        return key in self.data

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return 1
        return 0

    def ping(self):
        return True

# Conectar a Redis con fallback a MockRedis
try:
    cliente_redis = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD', ''),
        decode_responses=True
    )
    # Probar conexión
    cliente_redis.ping()
    print("✅ Conectado a Redis exitosamente")
except redis.ConnectionError:
    print("❌ Error de conexión a Redis, usando base de datos en memoria")
    cliente_redis = MockRedis()

# Función para limpiar claves inválidas
def limpiar_claves_invalidas():
    """Limpia las claves de libros que no son del tipo hash"""
    claves_libros = cliente_redis.keys('libro:*')
    contador = 0

    for clave in claves_libros:
        if cliente_redis.type(clave) != 'hash':
            print(f"Eliminando clave inválida: {clave}")
            cliente_redis.delete(clave)
            contador += 1

    return contador

# Definir tareas de Celery
@celery.task(name='app.enviar_correo_libro_agregado')
def enviar_correo_libro_agregado(titulo, autor, genero, email_destino):
    """Tarea asíncrona para enviar correo cuando se agrega un libro."""
    try:
        msg = Message(
            subject="Biblioteca: Nuevo libro agregado",
            recipients=[email_destino],
            body=(
                f"Hola,\n\n"
                f"Se ha agregado un nuevo libro a tu biblioteca personal:\n\n"
                f"Título: {titulo}\n"
                f"Autor: {autor}\n"
                f"Género: {genero}\n\n"
                f"Saludos,\n"
                f"Tu Biblioteca Personal"
            )
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False

@celery.task(name='app.enviar_correo_libro_eliminado')
def enviar_correo_libro_eliminado(titulo, autor, email_destino):
    """Tarea asíncrona para enviar correo cuando se elimina un libro."""
    try:
        msg = Message(
            subject="Biblioteca: Libro eliminado",
            recipients=[email_destino],
            body=(
                f"Hola,\n\n"
                f"Se ha eliminado el siguiente libro de tu biblioteca personal:\n\n"
                f"Título: {titulo}\n"
                f"Autor: {autor}\n\n"
                f"Saludos,\n"
                f"Tu Biblioteca Personal"
            )
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False

# Rutas
@app.route('/')
def inicio():
    libros = []
    # Obtener todas las claves de libros
    claves_libros = cliente_redis.keys('libro:*')

    for clave in claves_libros:
        try:
            # Verificar si la clave es un hash antes de usar hgetall
            if cliente_redis.type(clave) == 'hash':
                datos_libro = cliente_redis.hgetall(clave)
                datos_libro['id'] = clave.split(':')[1]
                libros.append(datos_libro)
            else:
                # Eliminar la clave incorrecta
                cliente_redis.delete(clave)
                print(f"Clave {clave} no es un hash, es {cliente_redis.type(clave)} - eliminada")
        except Exception as e:
            print(f"Error al procesar la clave {clave}: {str(e)}")
            continue

    return render_template('index.html', libros=libros)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_libro():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        genero = request.form.get('genero')
        estado = request.form.get('estado')
        email_usuario = os.getenv('DEFAULT_EMAIL', 'usuario@example.com')

        if not titulo or not autor:
            flash('Título y autor son campos obligatorios', 'danger')
            return render_template('agregar_libro.html')

        libro_id = str(uuid.uuid4())
        cliente_redis.hset(f'libro:{libro_id}',
                           mapping={
                               'titulo': titulo,
                               'autor': autor,
                               'genero': genero,
                               'estado': estado
                           })

        # Enviar correo de forma asíncrona
        celery.send_task('app.enviar_correo_libro_agregado', args=[titulo, autor, genero, email_usuario])

        flash('Libro agregado exitosamente', 'success')
        return redirect(url_for('inicio'))

    return render_template('agregar_libro.html')

@app.route('/eliminar/<libro_id>')
def eliminar_libro(libro_id):
    clave_libro = f'libro:{libro_id}'
    email_usuario = os.getenv('DEFAULT_EMAIL', 'usuario@example.com')

    # Añadir página de confirmación
    if request.args.get('confirmar') != 'true':
        if cliente_redis.exists(clave_libro):
            libro = cliente_redis.hgetall(clave_libro)
            return render_template('confirmar_eliminar.html', libro=libro, libro_id=libro_id)
        else:
            flash('Libro no encontrado', 'danger')
            return redirect(url_for('inicio'))

    if cliente_redis.exists(clave_libro):
        libro = cliente_redis.hgetall(clave_libro)
        cliente_redis.delete(clave_libro)

        # Enviar correo de forma asíncrona
        celery.send_task('app.enviar_correo_libro_eliminado',
            args=[libro.get('titulo', 'Desconocido'),
                  libro.get('autor', 'Desconocido'),
                  email_usuario])

        flash('Libro eliminado exitosamente', 'success')
    else:
        flash('Libro no encontrado', 'danger')

    return redirect(url_for('inicio'))

@app.route('/editar/<libro_id>', methods=['GET', 'POST'])
def editar_libro(libro_id):
    clave_libro = f'libro:{libro_id}'

    if not cliente_redis.exists(clave_libro):
        flash('Libro no encontrado', 'danger')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        genero = request.form.get('genero')
        estado = request.form.get('estado')

        if not titulo or not autor:
            flash('Título y autor son campos obligatorios', 'danger')
            libro = cliente_redis.hgetall(clave_libro)
            return render_template('editar_libro.html', libro=libro, libro_id=libro_id)

        cliente_redis.hset(clave_libro,
                           mapping={
                               'titulo': titulo,
                               'autor': autor,
                               'genero': genero,
                               'estado': estado
                           })

        flash('Libro actualizado exitosamente', 'success')
        return redirect(url_for('inicio'))

    libro = cliente_redis.hgetall(clave_libro)
    return render_template('editar_libro.html', libro=libro, libro_id=libro_id)

@app.route('/buscar')
def buscar():
    consulta = request.args.get('consulta', '').lower()
    libros = []

    if consulta:
        claves_libros = cliente_redis.keys('libro:*')

        for clave in claves_libros:
            try:
                # Verificar si la clave es un hash antes de usar hgetall
                if cliente_redis.type(clave) == 'hash':
                    datos_libro = cliente_redis.hgetall(clave)

                    # Verificar si la consulta está en título, autor o género
                    if (consulta in datos_libro.get('titulo', '').lower() or
                            consulta in datos_libro.get('autor', '').lower() or
                            consulta in datos_libro.get('genero', '').lower()):
                        datos_libro['id'] = clave.split(':')[1]
                        libros.append(datos_libro)
                else:
                    # Eliminar la clave incorrecta
                    cliente_redis.delete(clave)
                    print(f"Clave {clave} no es un hash, es {cliente_redis.type(clave)} - eliminada")
            except Exception as e:
                print(f"Error al procesar la clave {clave}: {str(e)}")
                continue

    return render_template('buscar.html', libros=libros, consulta=consulta)

@app.route('/mantenimiento')
def mantenimiento():
    claves_eliminadas = limpiar_claves_invalidas()
    flash(f'Se eliminaron {claves_eliminadas} claves inválidas', 'success')
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)