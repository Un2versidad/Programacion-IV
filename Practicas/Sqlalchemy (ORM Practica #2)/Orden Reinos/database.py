from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///orden_magica.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()