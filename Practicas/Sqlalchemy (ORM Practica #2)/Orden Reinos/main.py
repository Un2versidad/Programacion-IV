from modelos import crear_tablas
from operaciones import *

crear_tablas()

reino = crear_reino("Bosque de Eldur")
m1 = crear_mago("Luthien", 15, reino.id)
m2 = crear_mago("Derek", 8, reino.id)

h1 = crear_hechizo("Tormenta de hielo", "Ofensivo")
h2 = crear_hechizo("Muro de Viento", "Defensivo")

c1 = crear_criatura("Sombras", "Licántropo", reino.id)

asignar_hechizo_a_mago(m1.id, h1.id)
asignar_hechizo_a_mago(m2.id, h2.id)
asignar_criatura_a_mago(m1.id, c1.id)
asignar_criatura_a_mago(m2.id, c1.id)

print("Magos del reino: " + m1.nombre + ", " + m2.nombre)
print(c1.nombre + " cuidado por " + m1.nombre + " y " + m2.nombre)