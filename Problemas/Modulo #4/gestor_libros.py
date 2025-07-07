from pymongo import MongoClient
from bson.objectid import ObjectId

class GestorLibros:
    def __init__(self):
        # Conectar a MongoDB
        uri = "mongodb://admin:admin123@localhost:27017"
        try:
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
            # Probar conexión
            self.cliente.admin.command('ping')
            self.db = self.cliente["biblioteca_personal"]
            self.coleccion_libros = self.db["libros"]
        except Exception as e:
            raise ConnectionError(f"Error al conectar a MongoDB: {e}")

    def agregar_libro(self, titulo, autor, genero, estado_lectura):
        # Crear un nuevo documento de libro
        libro = {
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado_lectura": estado_lectura
        }

        # Insertar el documento en la colección
        resultado = self.coleccion_libros.insert_one(libro)
        return resultado.inserted_id

    def actualizar_libro(self, id_libro, titulo=None, autor=None, genero=None, estado_lectura=None):
        # Construir documento de actualización solo con los campos proporcionados
        datos_actualizacion = {}
        if titulo:
            datos_actualizacion["titulo"] = titulo
        if autor:
            datos_actualizacion["autor"] = autor
        if genero:
            datos_actualizacion["genero"] = genero
        if estado_lectura:
            datos_actualizacion["estado_lectura"] = estado_lectura

        # Actualizar el documento
        if datos_actualizacion:
            resultado = self.coleccion_libros.update_one(
                {"_id": ObjectId(id_libro)},
                {"$set": datos_actualizacion}
            )
            return resultado.modified_count > 0
        return False

    def eliminar_libro(self, id_libro):
        # Eliminar un libro por ID
        resultado = self.coleccion_libros.delete_one({"_id": ObjectId(id_libro)})
        return resultado.deleted_count > 0

    def listar_libros(self):
        # Obtener todos los libros de la colección
        return list(self.coleccion_libros.find())

    def buscar_libros(self, consulta, campo=None):
        # Buscar libros por título, autor o género
        if campo:
            # Buscar en un campo específico
            filtro_busqueda = {campo: {"$regex": consulta, "$options": "i"}}
        else:
            # Buscar en todos los campos
            filtro_busqueda = {
                "$or": [
                    {"titulo": {"$regex": consulta, "$options": "i"}},
                    {"autor": {"$regex": consulta, "$options": "i"}},
                    {"genero": {"$regex": consulta, "$options": "i"}}
                ]
            }
        return list(self.coleccion_libros.find(filtro_busqueda))