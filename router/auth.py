from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from database import get_db
from models.user import User
from schemas.auth import LoginRequest, ChangePasswordRequest
from auth.security import verify_password, hash_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
def login(datos: LoginRequest, request: Request, db=Depends(get_db)):
    from database import engine

    print("LOGIN_DIAG: base de datos =", engine.url.database)
    print("LOGIN_DIAG: servidor =", engine.url.host)
    print("LOGIN_DIAG: usuario recibido =", repr(datos.username))

    usuario = db.query(User).filter(User.username == datos.username).first()

    print("LOGIN_DIAG: usuario encontrado =", usuario is not None)

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    print("LOGIN_DIAG: usuario activo =", usuario.active)
    print("LOGIN_DIAG: longitud del hash =", len(usuario.password_hash or ""))

    if not usuario.active:
        raise HTTPException(
            status_code=403,
            detail="Usuario desactivado"
        )

    contrasena_correcta = verify_password(
        datos.password,
        usuario.password_hash
    )

    print("LOGIN_DIAG: contraseña coincide =", contrasena_correcta)

    if not contrasena_correcta:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    request.session["user_id"] = usuario.id
    request.session["username"] = usuario.username

    return {
        "mensaje": "Inicio de sesión correcto",
        "username": usuario.username
    }

@router.post("/change-password")
def cambiar_contrasena(
    datos: ChangePasswordRequest,
    request: Request,
    db=Depends(get_db)
):
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Debe iniciar sesión.")

    usuario = db.query(User).filter(User.id == user_id).first()


    if usuario is None or not usuario.active:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Sesión no válida.")

    if not verify_password(datos.current_password, usuario.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")

    if datos.current_password == datos.new_password:
        raise HTTPException(
            status_code=400,
            detail="La nueva contraseña debe ser diferente a la actual."
        )

    usuario.password_hash = hash_password(datos.new_password)
    db.commit()

    return {"mensaje": "Contraseña actualizada correctamente."}


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
