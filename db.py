from model import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///chatdb.db')

session = Session(bind=engine)

Base.metadata.create_all(engine)
