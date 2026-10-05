"""Migra los datos actuales de salon.db (SQLite) a PostgreSQL.

Uso:
    1. Definir DATABASE_URL apuntando a PostgreSQL.
    2. Ejecutar: python migrar_sqlite_a_postgres.py

El script conserva los IDs para mantener las relaciones entre clientes,
servicios y pagos.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database import Base
from models.clients import Client
from models.service import Service
from models.payment import Payment
from models.user import User


SQLITE_URL = "sqlite:///./salon.db"
POSTGRES_URL = os.getenv("DATABASE_URL")


if not POSTGRES_URL:
    raise RuntimeError(
        "Define DATABASE_URL con la conexión de PostgreSQL antes de migrar."
    )


if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )


if not POSTGRES_URL.startswith("postgresql"):
    raise RuntimeError(
        "DATABASE_URL debe apuntar a PostgreSQL para ejecutar esta migración."
    )


sqlite_engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False}
)

postgres_engine = create_engine(
    POSTGRES_URL,
    pool_pre_ping=True
)


Base.metadata.create_all(bind=postgres_engine)


SQLiteSession = sessionmaker(bind=sqlite_engine)
PostgresSession = sessionmaker(bind=postgres_engine)


source = SQLiteSession()
target = PostgresSession()


try:
    # Limpieza controlada del destino para permitir repetir la migración.
    target.execute(text("DELETE FROM payments"))
    target.execute(text("DELETE FROM services"))
    target.execute(text("DELETE FROM clients"))
    target.execute(text("DELETE FROM users"))

    target.commit()


    # Leer datos desde SQLite
    users = source.query(User).all()
    clients = source.query(Client).all()
    services = source.query(Service).all()
    payments = source.query(Payment).all()


    # Migrar usuarios
    for item in users:
        target.add(
            User(
                id=item.id,
                username=item.username,
                password_hash=item.password_hash,
                active=item.active
            )
        )


    # Migrar clientes
    for item in clients:
        target.add(
            Client(
                id=item.id,
                name=item.name,
                phone=item.phone,
                email=item.email
            )
        )


    # Migrar servicios
    for item in services:
        target.add(
            Service(
                id=item.id,
                name=item.name,
                price=item.price,
                active=item.active
            )
        )


    # Migrar pagos
    for item in payments:
        target.add(
            Payment(
                id=item.id,
                client_id=item.client_id,
                service_id=item.service_id,
                amount=item.amount,
                payment_method=item.payment_method,
                date=item.date
            )
        )


    target.commit()


    # Sincronizar las secuencias de PostgreSQL
    for table in ("users", "clients", "services", "payments"):
        target.execute(
            text(
                f"SELECT setval("
                f"pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1), "
                f"true)"
            )
        )


    target.commit()


    print("Migración completada correctamente.")
    print(f"Usuarios: {len(users)}")
    print(f"Clientes: {len(clients)}")
    print(f"Servicios: {len(services)}")
    print(f"Pagos: {len(payments)}")


except Exception:
    target.rollback()
    raise


finally:
    source.close()
    target.close()

    