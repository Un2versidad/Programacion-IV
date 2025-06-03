from modelos import Reino, Mago, Hechizo, Criatura
from database import session

def crear_reino(nombre):
    r = Reino(nombre=nombre)
    session.add(r)
    session.commit()
    return r

def crear_mago(nombre, nivel, reino_id):
    m = Mago(nombre=nombre, nivel=nivel, reino_id=reino_id)
    session.add(m)
    session.commit()
    return m

def crear_hechizo(nombre, tipo):
    h = Hechizo(nombre=nombre, tipo=tipo)
    session.add(h)
    session.commit()
    return h

def crear_criatura(nombre, especie, reino_id):
    c = Criatura(nombre=nombre, especie=especie, reino_id=reino_id)
    session.add(c)
    session.commit()
    return c

def asignar_hechizo_a_mago(mago_id, hechizo_id):
    mago = session.get(Mago, mago_id)
    hechizo = session.get(Hechizo, hechizo_id)
    if hechizo not in mago.hechizos:
        mago.hechizos.append(hechizo)
        session.commit()

def asignar_criatura_a_mago(mago_id, criatura_id):
    mago = session.get(Mago, mago_id)
    criatura = session.get(Criatura, criatura_id)
    if criatura not in mago.criaturas:
        mago.criaturas.append(criatura)
        session.commit()