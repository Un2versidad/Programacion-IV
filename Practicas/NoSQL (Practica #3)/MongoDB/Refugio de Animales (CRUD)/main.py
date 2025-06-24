# CRUD Create, Read, Update, Delete
import pymongo
import colorama
import tabulate

# Initialize Mongo_DB client with connection URI
uri = "mongodb://admin:admin123@localhost:27017"

try:
    # Connect to MongoDB
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print(colorama.Fore.GREEN + "🛜 Pong! Connected to MongoDB successfully.")

    # Access the database and collection
    db = client['refugio']
    collection = client['animales']

    # Create a new collection if it doesn't exist
    if 'animales' not in db.list_collection_names():
        collection = db.create_collection('animales')
    else:
        collection = db['animales']
        print("✔️ Collection 'animales' is ready.")

    # Functions for CRUD operations (Agregar, Leer, Actualizar, Eliminar)

    # Function to add an animal
    def agregar_animal():
        animal = {
            "nombre": input("Nombre del animal: "),
            "especie": input("Especie del animal: "),
            "edad": int(input("Edad del animal: ")),
            "continente": input("Continente del animal: "),
            "peligro": input("Peligro de extinción (Sí/No): ").lower() == 'si'
        }
        result = collection.insert_one(animal)
        print(f"Animal agregado con ID: {result.inserted_id}")

    # Function to show an animal by ID
    def mostrar_todos_los_animales():
        animales = list(collection.find())
        if not animales:
            print("No hay animales en la colección.")
            return
        tabla = []
        for animal in animales:
            tabla.append([
                str(animal['_id']),
                animal['nombre'],
                animal['especie'],
                animal['edad'],
                animal['continente'],
                'Sí' if animal['peligro'] else 'No'
            ])
        headers = ["ID", "Nombre", "Especie", "Edad", "Continente", "Peligro de extinción"]
        print(tabulate.tabulate(tabla, headers, tablefmt="fancy_grid"))

    # Function to update an animal by ID
    def actualizar_animal():
        animal_id = input("ID del animal a actualizar: ")
        update_fields = {}
        if input("Actualizar nombre? (Sí/No): ").lower() == 'sí':
            update_fields['nombre'] = input("Nuevo nombre: ")
        if input("Actualizar especie? (Sí/No): ").lower() == 'sí':
            update_fields['especie'] = input("Nueva especie: ")
        if input("Actualizar edad? (Sí/No): ").lower() == 'sí':
            update_fields['edad'] = int(input("Nueva edad: "))
        if input("Actualizar continente? (Sí/No): ").lower() == 'sí':
            update_fields['continente'] = input("Nuevo continente: ")
        if input("Actualizar peligro de extinción? (Sí/No): ").lower() == 'sí':
            update_fields['peligro'] = input("Peligro de extinción (Sí/No): ").lower() == 'sí'

        result = collection.update_one({'_id': pymongo.ObjectId(animal_id)}, {'$set': update_fields})
        if result.modified_count > 0:
            print(f"Animal con ID {animal_id} actualizado.")
        else:
            print(f"No se encontró un animal con ID {animal_id} o no se realizaron cambios.")

    # Function to delete an animal by ID
    def eliminar_animal():
        animal_id = input("ID del animal a eliminar: ")
        result = collection.delete_one({'_id': pymongo.ObjectId(animal_id)})
        if result.deleted_count > 0:
            print(f"Animal con ID {animal_id} eliminado.")
        else:
            print(f"No se encontró un animal con ID {animal_id}.")

    # Main menu for CRUD operations
    while True:
        print(colorama.Fore.WHITE + "\nMenú de operaciones CRUD:" + colorama.Style.RESET_ALL)
        menu_items = [
            ["1", "Agregar un animal"],
            ["2", "Mostrar todos los animales"],
            ["3", "Actualizar un animal"],
            ["4", "Eliminar un animal"],
            ["5", "Salir"]
        ]
        print(tabulate.tabulate(menu_items, headers=["Opción", "Descripción"], tablefmt="fancy_grid"))

        choice = input("Seleccione una opción: ")

        if choice == '1':
            agregar_animal()
        elif choice == '2':
            mostrar_todos_los_animales()
        elif choice == '3':
            actualizar_animal()
        elif choice == '4':
            eliminar_animal()
        elif choice == '5':
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida, por favor intente de nuevo.")

except ConnectionError as e:
    print(colorama.Fore.RED + "❌ Failed to connect to MongoDB. Please check your connection settings. Error:", e)