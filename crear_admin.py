from database import SessionLocal
from models.user import User
from auth.security import hash_password


db = SessionLocal()


usuario_existente = (
    db.query(User)
    .filter(User.username == "admin")
    .first()
)


if usuario_existente:
    print("El usuario admin ya existe.")
else:
    nuevo_usuario = User(
        username="admin",
        password_hash=hash_password("Admin123"),
        active=True
    )

    db.add(nuevo_usuario)
    db.commit()

    print("Usuario administrador creado correctamente.")
    print("Usuario: admin")
    print("Contraseña: Admin123")


db.close()