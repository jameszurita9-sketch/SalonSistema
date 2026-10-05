from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models.service import Service
from schemas.service import ServiceCreate


router = APIRouter(
    prefix="/services",
    tags=["Servicios"]
)


@router.get("/")
def listar_servicios(
    db=Depends(get_db)
):

    servicios = (
        db.query(Service)
        .filter(Service.active == True)
        .all()
    )

    return servicios


@router.post("/")
def crear_servicio(
    service: ServiceCreate,
    db=Depends(get_db)
):

    nuevo_servicio = Service(
        name=service.name,
        price=service.price,
        active=True
    )

    try:

        db.add(nuevo_servicio)
        db.commit()
        db.refresh(nuevo_servicio)

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo crear el servicio"
        )

    return nuevo_servicio


@router.get("/{service_id}")
def obtener_servicio(
    service_id: int,
    db=Depends(get_db)
):

    servicio = (
        db.query(Service)
        .filter(Service.id == service_id)
        .first()
    )

    if servicio is None:

        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    return servicio


@router.put("/{service_id}")
def actualizar_servicio(
    service_id: int,
    service: ServiceCreate,
    db=Depends(get_db)
):

    servicio = (
        db.query(Service)
        .filter(Service.id == service_id)
        .first()
    )

    if servicio is None:

        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    if not servicio.active:

        raise HTTPException(
            status_code=400,
            detail=(
                "No se puede modificar "
                "un servicio desactivado"
            )
        )

    servicio.name = service.name
    servicio.price = service.price

    try:

        db.commit()
        db.refresh(servicio)

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el servicio"
        )

    return servicio


@router.delete("/{service_id}")
def eliminar_servicio(
    service_id: int,
    db=Depends(get_db)
):

    servicio = (
        db.query(Service)
        .filter(Service.id == service_id)
        .first()
    )

    if servicio is None:

        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    if not servicio.active:

        raise HTTPException(
            status_code=400,
            detail="El servicio ya está desactivado"
        )

    servicio.active = False

    try:

        db.commit()
        db.refresh(servicio)

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo desactivar el servicio"
        )

    return {
        "mensaje": "Servicio desactivado correctamente"
    }