from sqlalchemy import Column, String, ForeignKey, Table, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import engine

Base = declarative_base()

# Tabla intermedia para la relación muchos a muchos entre magos y hechizos
magos_hechizos = Table('magos_hechizos', Base.metadata,
    Column('mago_id', Integer, ForeignKey('magos.id')),
    Column('hechizo_id', Integer, ForeignKey('hechizos.id'))
)

# Tabla intermedia para la relación muchos a muchos entre magos y criaturas
magos_criaturas = Table('magos_criaturas', Base.metadata,
    Column('mago_id', Integer, ForeignKey('magos.id')),
    Column('criatura_id', Integer, ForeignKey('criaturas.id'))
)

class Reino(Base):
    __tablename__ = 'reinos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    magos = relationship("Mago", back_populates="reino")
    criaturas = relationship("Criatura", back_populates="reino")

class Mago(Base):
    __tablename__ = 'magos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    nivel = Column(Integer)
    reino_id = Column(Integer, ForeignKey('reinos.id'))

    reino = relationship("Reino", back_populates="magos")
    hechizos = relationship("Hechizo", secondary=magos_hechizos, back_populates="magos")
    criaturas = relationship("Criatura", secondary=magos_criaturas, back_populates="cuidadores")

class Hechizo(Base):
    __tablename__ = 'hechizos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    tipo = Column(String)

    magos = relationship("Mago", secondary=magos_hechizos, back_populates="hechizos")

class Criatura(Base):
    __tablename__ = 'criaturas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    especie = Column(String)
    reino_id = Column(Integer, ForeignKey('reinos.id'))

    reino = relationship("Reino", back_populates="criaturas")
    cuidadores = relationship("Mago", secondary=magos_criaturas, back_populates="criaturas")

def crear_tablas():
    Base.metadata.create_all(engine)