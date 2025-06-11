from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from config.config_loader import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

sessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
