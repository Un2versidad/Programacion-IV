from sqlalchemy import Column, String, ForeignKey, Table, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import engine

Base = declarative_base()

Owner_mascota = Table('owner_mascotas', Base.metadata,
    Column('owner_id', Integer, ForeignKey('owner.id')),
    Column('mascota_id', Integer, ForeignKey('mascotas.id'))
)

class Owner(Base):
    __tablename__ = 'owner'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    mascotas = relationship("Mascota", back_populates="owner")

class Mascota(Base):
    __tablename__ = 'mascotas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    especie = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('owner.id'))
    owner = relationship("Owner", back_populates="mascotas")

def crear_tablas():
    Base.metadata.create_all(engine)