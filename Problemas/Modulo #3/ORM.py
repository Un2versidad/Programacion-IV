import os
import configparser
from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class EstadoLectura(Enum):
    NO_LEIDO = "No leído"
    LEYENDO = "Leyendo"
    LEIDO = "Leído"

class Libro(Base):
    __tablename__ = 'libros'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(255), nullable=False)
    autor = Column(String(255), nullable=False)
    genero = Column(String(100))
    estado = Column(String(50), default=EstadoLectura.NO_LEIDO.value)

def cargar_config_bd(archivo_config='db_config.ini'):
    """Cargar configuración de base de datos desde un archivo o crear uno si no existe"""
    if not os.path.exists(archivo_config):
        print(f"Archivo de configuración {archivo_config} no encontrado. Creando uno con valores predeterminados...")
        config = configparser.ConfigParser()
        config['Database'] = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'database': 'biblioteca'
        }

        try:
            with open(archivo_config, 'w') as f:
                config.write(f)
            print(f"Archivo {archivo_config} creado correctamente.")
            print("IMPORTANTE: Edite este archivo con sus credenciales reales antes de continuar.")
            respuesta = input("¿Desea editar el archivo ahora? (s/n): ")
            if respuesta.lower() == 's':
                os.system(f"notepad {archivo_config}")
        except Exception as e:
            print(f"Error al crear el archivo de configuración: {e}")
            raise

    config = configparser.ConfigParser()
    config.read(archivo_config)

    if 'Database' not in config:
        raise ValueError("Sección Database no encontrada en el archivo de configuración")

    db_config = config['Database']
    return {
        'usuario': db_config.get('user', 'root'),
        'contraseña': db_config.get('password', ''),
        'host': db_config.get('host', 'localhost'),
        'base_datos': db_config.get('database', 'biblioteca')
    }

def crear_bd_si_no_existe(user, password, host, base_datos):
    """Crear la base de datos si no existe"""
    try:
        # Conectar a MySQL
        url = f"mysql+pymysql://{user}:{password}@{host}/"
        motor_temp = create_engine(url)

        # Ejecutar la creación de la base de datos
        with motor_temp.begin() as conexion:
            conexion.execute(text(f"CREATE DATABASE IF NOT EXISTS `{base_datos}`"))

        print(f"Base de datos '{base_datos}' creada o verificada correctamente.")
        return True
    except SQLAlchemyError as e:
        print(f"Error al crear la base de datos: {e}")
        return False

def obtener_motor(user, password, host, base_datos):
    """Crear y devolver el motor de base de datos SQLAlchemy"""
    url = f"mysql+pymysql://{user}:{password}@{host}/{base_datos}"
    return create_engine(url, echo=False)

def inicializar_bd(motor):
    """Crear todas las tablas definidas en el modelo"""
    Base.metadata.create_all(motor)

def obtener_sesion(motor):
    """Crear y devolver una sesión de SQLAlchemy"""
    session = sessionmaker(bind=motor)
    return session()

def conectar_bd(config=None):
    """Conectar a la base de datos usando la configuración proporcionada"""
    try:
        if config is None:
            config = cargar_config_bd()

        # Crear la base de datos si no existe
        if not crear_bd_si_no_existe(
                config['usuario'],
                config['contraseña'],
                config['host'],
                config['base_datos']
        ):
            raise Exception("No se pudo crear o verificar la base de datos")

        # Conectar a la base de datos
        motor = obtener_motor(
            config['usuario'],
            config['contraseña'],
            config['host'],
            config['base_datos']
        )
        inicializar_bd(motor)
        return motor
    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        raise


def agregar_libro(sesion, titulo, autor, genero, estado=EstadoLectura.NO_LEIDO.value):
    """Agregar un nuevo libro a la base de datos"""
    libro = Libro(titulo=titulo, autor=autor, genero=genero, estado=estado)
    sesion.add(libro)
    sesion.commit()
    return libro

def obtener_todos_libros(sesion):
    """Obtener todos los libros de la base de datos"""
    return sesion.query(Libro).all()

def buscar_libros(sesion, criterios):
    """Buscar libros según criterios específicos"""
    consulta = sesion.query(Libro)

    if 'titulo' in criterios:
        consulta = consulta.filter(Libro.titulo.like(f"%{criterios['titulo']}%"))
    if 'autor' in criterios:
        consulta = consulta.filter(Libro.autor.like(f"%{criterios['autor']}%"))
    if 'genero' in criterios:
        consulta = consulta.filter(Libro.genero.like(f"%{criterios['genero']}%"))
    if 'estado' in criterios:
        consulta = consulta.filter(Libro.estado == criterios['estado'])

    return consulta.all()

def actualizar_libro(sesion, id_libro, datos):
    """Actualizar información de un libro existente"""
    libro = sesion.query(Libro).filter(Libro.id == id_libro).first()
    if not libro:
        return None

    for campo, valor in datos.items():
        setattr(libro, campo, valor)

    sesion.commit()
    return libro

def eliminar_libro(sesion, id_libro):
    """Eliminar un libro de la base de datos"""
    libro = sesion.query(Libro).filter(Libro.id == id_libro).first()
    if not libro:
        return False

    sesion.delete(libro)
    sesion.commit()
    return True