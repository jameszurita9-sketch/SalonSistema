from fastapi import APIRouter, HTTPException, Depends

from database import get_db
from models.payment import Payment
from models.clients import Client
from models.service import Service
from schemas.payment import PaymentCreate, PaymentResponse

from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter(
    prefix="/payments",
    tags=["Pagos"]
)


@router.get(
    "/",
    response_model=list[PaymentResponse]
)
def listar_pagos(
    db=Depends(get_db)
):

    pagos = db.query(Payment).all()

    resultado = []

    for pago in pagos:

        resultado.append({
            "id": pago.id,

            "cliente": (
                pago.client.name
                if pago.client
                else "Cliente ocasional"
            ),

            "servicio": pago.service.name,

            "monto": pago.amount,

            "metodo_pago": pago.payment_method,

            "fecha": pago.date
        })

    return resultado


@router.post("/")
def crear_pago(
    payment: PaymentCreate,
    db=Depends(get_db)
):

    servicio = (
        db.query(Service)
        .filter(Service.id == payment.service_id)
        .first()
    )

    if servicio is None:

        raise HTTPException(
            status_code=404,
            detail="El servicio no existe"
        )

    if not servicio.active:

        raise HTTPException(
            status_code=400,
            detail="El servicio está desactivado"
        )

    if payment.client_id is not None:

        cliente = (
            db.query(Client)
            .filter(Client.id == payment.client_id)
            .first()
        )

        if cliente is None:

            raise HTTPException(
                status_code=404,
                detail="El cliente no existe"
            )

    nuevo_pago = Payment(
        client_id=payment.client_id,
        service_id=payment.service_id,
        amount=payment.amount,
        payment_method=payment.payment_method
    )

    try:

        db.add(nuevo_pago)
        db.commit()
        db.refresh(nuevo_pago)

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar el pago"
        )

    return nuevo_pago


@router.get("/summary")
def resumen_ingresos(
    db=Depends(get_db)
):

    ahora = datetime.now()

    inicio_dia = datetime(
        ahora.year,
        ahora.month,
        ahora.day
    )

    inicio_semana = (
        inicio_dia -
        timedelta(days=ahora.weekday())
    )

    inicio_mes = datetime(
        ahora.year,
        ahora.month,
        1
    )

    total_dia = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= inicio_dia
        )
        .scalar() or 0
    )

    efectivo_dia = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= inicio_dia,
            Payment.payment_method == "Efectivo"
        )
        .scalar() or 0
    )

    qr_dia = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= inicio_dia,
            Payment.payment_method == "QR"
        )
        .scalar() or 0
    )

    total_semana = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= inicio_semana
        )
        .scalar() or 0
    )

    total_mes = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= inicio_mes
        )
        .scalar() or 0
    )

    return {
        "total_hoy": total_dia,
        "efectivo_hoy": efectivo_dia,
        "qr_hoy": qr_dia,
        "total_semana": total_semana,
        "total_mes": total_mes
    }


@router.get("/{payment_id}")
def obtener_pago(
    payment_id: int,
    db=Depends(get_db)
):

    pago = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if pago is None:

        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    return {
        "id": pago.id,

        "cliente": (
            pago.client.name
            if pago.client
            else "Cliente ocasional"
        ),

        "servicio": pago.service.name,

        "monto": pago.amount,

        "metodo_pago": pago.payment_method,

        "fecha": pago.date
    }    