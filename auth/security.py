import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def get_secret_key() -> str:
    """Obtiene la clave de sesión desde el entorno.

    En desarrollo permite un valor temporal para no romper el proyecto existente.
    En producción, SALON_ENV=production obliga a definir SALON_SECRET_KEY.
    """
    key = os.getenv("SALON_SECRET_KEY")
    environment = os.getenv("SALON_ENV", "development").lower()

    if environment == "production" and not key:
        raise RuntimeError(
            "SALON_SECRET_KEY debe estar definida cuando SALON_ENV=production."
        )

    return key or "clave-temporal-salon-sistema"


SECRET_KEY = get_secret_key()
