from pathlib import Path
import os

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from database import create_tables
from auth.security import SECRET_KEY
from router.services import router as services_router
from router.clients import router as clients_router
from router.payment import router as payments_router
from router.reports import router as reports_router
from router.auth import router as auth_router


app = FastAPI(
    title="SalónSistema",
    description="Sistema de gestión para salón de belleza y barbería",
    version="1.0.0"
)

create_tables()

app.include_router(services_router)
app.include_router(clients_router)
app.include_router(payments_router)
app.include_router(reports_router)
app.include_router(auth_router)


@app.middleware("http")
async def proteger_sistema(request: Request, call_next):
    ruta = request.url.path

    rutas_publicas = {
        "/login",
        "/auth/login",
        "/auth/logout",
        "/docs",
        "/openapi.json",
        "/redoc"
    }

    if ruta in rutas_publicas:
        return await call_next(request)

    usuario_id = request.session.get("user_id")

    if usuario_id is None:
        if ruta == "/auth/change-password":
            return JSONResponse(
                status_code=401,
                content={"detail": "Debe iniciar sesión."}
            )

        if ruta.startswith(("/clients", "/services", "/payments", "/reports")):
            return JSONResponse(
                status_code=401,
                content={"detail": "Debe iniciar sesión para acceder."}
            )

        if ruta == "/":
            return RedirectResponse(url="/login", status_code=303)

    return await call_next(request)


app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="salon_session",
    max_age=60 * 60 * 8,
    same_site="lax",
    https_only=os.getenv("SALON_ENV", "development").lower() == "production"
)


@app.get("/login")
def pagina_login():
    archivo_login = Path(__file__).resolve().parent / "templates" / "login.html"
    return FileResponse(path=archivo_login, media_type="text/html")


@app.get("/")
def inicio():
    archivo_index = Path(__file__).resolve().parent / "templates" / "index.html"
    return FileResponse(path=archivo_index, media_type="text/html")
