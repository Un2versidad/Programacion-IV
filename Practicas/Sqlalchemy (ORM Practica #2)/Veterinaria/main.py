from modelos import crear_tablas
from operaciones import *
from database import session
from tabulate import tabulate

# Crear las tablas en la base de datos
crear_tablas()

# Crear dueños y mascotas
dueno1 = Owner(nombre="Carlos Pérez")
dueno2 = Owner(nombre="Melanie Sanchez")
session.add_all([dueno1, dueno2])
session.commit()

print("\nDueños registrados:")
print(tabulate([[dueno1.id, dueno1.nombre], [dueno2.id, dueno2.nombre]],headers=["ID", "Nombre"], tablefmt="grid"))

mascota1 = adoptar_mascota("Tomi", "Perro", dueno1.id)
mascota2 = adoptar_mascota("Kira", "Gato", dueno1.id)
mascota3 = adoptar_mascota("Piolín", "Ave", dueno2.id)

# Mostrar las mascotas adoptadas en formato tabular
mascotas_adoptadas = [
    [mascota1.nombre, mascota1.especie, dueno1.nombre],
    [mascota2.nombre, mascota2.especie, dueno1.nombre],
    [mascota3.nombre, mascota3.especie, dueno2.nombre]
]
print("\nMascotas adoptadas:")
print(tabulate(mascotas_adoptadas, headers=["Nombre", "Especie", "Dueño"], tablefmt="grid"))

# Mostrar las mascotas de cada dueño (Inicial antes de Reasignar)
print("\n-------------------------------------------------------------------")
print("   Lista #1 de mascotas de cada dueño (Inicial antes de Reasignar)")
print("-------------------------------------------------------------------")

# Mostrar mascotas del primer dueño en tabla
mascotas_dueno1 = [[mascota.nombre, mascota.especie] for mascota in dueno1.mascotas]
print(f"\nMascotas de {dueno1.nombre}:")
print(tabulate(mascotas_dueno1, headers=["Nombre", "Especie"], tablefmt="grid"))

# Mostrar mascotas del segundo dueño en tabla
mascotas_dueno2 = [[mascota.nombre, mascota.especie] for mascota in dueno2.mascotas]
print(f"\nMascotas de {dueno2.nombre}:")
print(tabulate(mascotas_dueno2, headers=["Nombre", "Especie"], tablefmt="grid"))

# Reasignar una mascota a otro dueño
print(f"\nReasignando {mascota2.nombre} de {dueno1.nombre} a {dueno2.nombre}...")
asignar_mascota_a_dueno(mascota2.id, dueno2.id)

# Limpiar la sesión para evitar problemas de caché
session.expire_all()

dueno1 = session.query(Owner).filter_by(id=dueno1.id).first()
dueno2 = session.query(Owner).filter_by(id=dueno2.id).first()
mascota2 = session.query(Mascota).filter_by(id=mascota2.id).first()

print(f"{mascota2.nombre} ahora pertenece a {mascota2.owner.nombre}")

# Mostrar las mascotas de cada dueño (Después de Reasignar)
print("\n-------------------------------------------------------------------")
print("     Lista #2 de mascotas de cada dueño (Después de Reasignar)")
print("-------------------------------------------------------------------")

# Mostrar mascotas actualizadas del primer dueño en tabla
mascotas_dueno1_despues = [[mascota.nombre, mascota.especie] for mascota in dueno1.mascotas]
print(f"\nMascotas de {dueno1.nombre}:")
print(tabulate(mascotas_dueno1_despues, headers=["Nombre", "Especie"], tablefmt="grid"))

# Mostrar mascotas actualizadas del segundo dueño en tabla
mascotas_dueno2_despues = [[mascota.nombre, mascota.especie] for mascota in dueno2.mascotas]
print(f"\nMascotas de {dueno2.nombre}:")
print(tabulate(mascotas_dueno2_despues, headers=["Nombre", "Especie"], tablefmt="grid"))