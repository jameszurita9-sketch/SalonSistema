from fastapi import APIRouter, HTTPException, Depends

from database import get_db
from models.clients import Client
from models.payment import Payment
from schemas.client import ClientCreate, ClientResponse


router = APIRouter(
    prefix="/clients",
    tags=["Clientes"]
)


@router.get("/", response_model=list[ClientResponse])
def listar_clientes(
    db=Depends(get_db)
):

    clientes = db.query(Client).all()

    return clientes


@router.post("/", response_model=ClientResponse)
def crear_cliente(
    client: ClientCreate,
    db=Depends(get_db)
):

    nuevo_cliente = Client(
        name=client.name,
        phone=client.phone,
        email=client.email
    )

    try:

        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo crear el cliente"
        )

    return nuevo_cliente


@router.get(
    "/{client_id}",
    response_model=ClientResponse
)
def obtener_cliente(
    client_id: int,
    db=Depends(get_db)
):

    cliente = (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )

    if cliente is None:

        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return cliente


@router.put(
    "/{client_id}",
    response_model=ClientResponse
)
def actualizar_cliente(
    client_id: int,
    client: ClientCreate,
    db=Depends(get_db)
):

    cliente = (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )

    if cliente is None:

        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    cliente.name = client.name
    cliente.phone = client.phone
    cliente.email = client.email

    try:

        db.commit()
        db.refresh(cliente)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el cliente"
        )

    return cliente


@router.delete("/{client_id}")
def eliminar_cliente(
    client_id: int,
    db=Depends(get_db)
):

    cliente = (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )

    if cliente is None:

        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    tiene_pagos = (
        db.query(Payment)
        .filter(Payment.client_id == client_id)
        .first()
    )

    if tiene_pagos is not None:

        raise HTTPException(
            status_code=400,
            detail=(
                "No se puede eliminar el cliente "
                "porque tiene pagos registrados."
            )
        )

    try:

        db.delete(cliente)
        db.commit()

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar el cliente"
        )

    return {
        "mensaje": "Cliente eliminado correctamente"
    }