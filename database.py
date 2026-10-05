import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Desarrollo: SQLite sigue siendo el valor por defecto para no romper
# la instalación actual. Producción: usar DATABASE_URL con PostgreSQL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./salon.db")

# Algunos proveedores entregan postgres://; SQLAlchemy moderno usa postgresql://.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def create_tables():
    from models.clients import Client
    from models.service import Service
    from models.payment import Payment
    from models.user import User

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    print("Tablas creadas correctamente")
