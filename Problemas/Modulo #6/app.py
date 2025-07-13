from flask import Flask, render_template, request, redirect, url_for, flash
import redis
import uuid
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave_desarrollo')

# Conectar a KeyDB
cliente_redis = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD', ''),
    decode_responses=True
)

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

        if not titulo or not autor:
            flash('Título y autor son campos obligatorios', 'error')
            return render_template('agregar_libro.html')

        libro_id = str(uuid.uuid4())
        cliente_redis.hset(f'libro:{libro_id}',
                          mapping={
                              'titulo': titulo,
                              'autor': autor,
                              'genero': genero,
                              'estado': estado
                          })

        flash('Libro agregado exitosamente', 'success')
        return redirect(url_for('inicio'))

    return render_template('agregar_libro.html')

@app.route('/editar/<libro_id>', methods=['GET', 'POST'])
def editar_libro(libro_id):
    clave_libro = f'libro:{libro_id}'

    if not cliente_redis.exists(clave_libro):
        flash('Libro no encontrado', 'error')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        genero = request.form.get('genero')
        estado = request.form.get('estado')

        if not titulo or not autor:
            flash('Título y autor son campos obligatorios', 'error')
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

@app.route('/eliminar/<libro_id>')
def eliminar_libro(libro_id):
    clave_libro = f'libro:{libro_id}'

    if cliente_redis.exists(clave_libro):
        cliente_redis.delete(clave_libro)
        flash('Libro eliminado exitosamente', 'success')
    else:
        flash('Libro no encontrado', 'error')

    return redirect(url_for('inicio'))

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