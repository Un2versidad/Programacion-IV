from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '1w3r5y7i'

# Diccionario para llevar conteo por token
contador_llamadas = {}

def token_requerido(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return jsonify({'mensaje': 'Token es requerido!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'mensaje': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensaje': 'Token inválido!'}), 401
        request.token = token  # Guardamos el token en request para uso posterior
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'mensaje': 'Credenciales faltantes!'}), 401
    if auth['username'] != 'admin' or auth['password'] != '1234':
        return jsonify({'mensaje': 'Credenciales incorrectas!'}), 401

    token = jwt.encode({
        'user': auth['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    # Inicializamos el contador en 0 para este token
    contador_llamadas[token] = 0

    return jsonify({'token': token}), 200

@app.route('/crear_data', methods=['POST'])
def crear_data():
    data = request.json
    return jsonify({'mensaje': 'Datos creados correctamente!', 'data': data}), 201

@app.route('/set_secreto', methods=['GET'])
def set_secreto():
    return jsonify({'mensaje': 'Utiliza el header X-Secreto con el valor: super_secret_value'}), 200

@app.route('/eliminar_data', methods=['DELETE'])
@token_requerido
def eliminar_data():
    token = request.token
    data_id = request.args.get('id')
    if not data_id:
        return jsonify({'mensaje': 'Falta el ID del dato a eliminar!'}), 400

    # Incrementar contador por token
    contador_llamadas[token] += 1

    # Validar límite de 3
    if contador_llamadas[token] > 3:
        return jsonify({'mensaje': 'Límite de llamadas alcanzado!'}), 429

    secreto_header = request.headers.get('X-Secreto')
    if secreto_header:
        return jsonify({'mensaje': f'Dato eliminado con secreto: {secreto_header}'}), 200
    else:
        return jsonify({'mensaje': 'Datos eliminados sin secreto.'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
