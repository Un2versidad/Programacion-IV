from modelos import Mascota, Owner
from database import session

def adoptar_mascota(nombre, especie, owner_id):
    mascota = Mascota(nombre=nombre, especie=especie, owner_id=owner_id)
    session.add(mascota)
    session.commit()
    return mascota

def asignar_mascota_a_dueno(mascota_id, owner_id):
    mascota = session.query(Mascota).filter_by(id=mascota_id).first()
    if mascota:
        mascota.owner_id = owner_id
        session.commit()
    return True