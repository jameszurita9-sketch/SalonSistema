from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from models.payment import Payment
from models.service import Service

from sqlalchemy import func
from datetime import datetime, timedelta


router = APIRouter(
    prefix="/reports",
    tags=["Reportes"]
)


@router.get("/summary")
def reporte_general(
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

    hoy = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.date >= inicio_dia)
        .scalar() or 0
    )

    semana = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.date >= inicio_semana)
        .scalar() or 0
    )

    mes = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.date >= inicio_mes)
        .scalar() or 0
    )

    efectivo = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= inicio_dia,
            Payment.payment_method == "Efectivo"
        )
        .scalar() or 0
    )

    qr = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= inicio_dia,
            Payment.payment_method == "QR"
        )
        .scalar() or 0
    )

    servicios_hoy = (
        db.query(func.count(Payment.id))
        .filter(Payment.date >= inicio_dia)
        .scalar() or 0
    )

    return {
        "hoy": float(hoy),
        "semana": float(semana),
        "mes": float(mes),
        "efectivo_hoy": float(efectivo),
        "qr_hoy": float(qr),
        "servicios_hoy": servicios_hoy
    }


@router.get("/services")
def ingresos_por_servicio(
    db=Depends(get_db)
):

    resultados = (
        db.query(
            Service.name,
            func.count(Payment.id),
            func.sum(Payment.amount)
        )
        .join(
            Payment,
            Payment.service_id == Service.id
        )
        .group_by(Service.id)
        .all()
    )

    respuesta = []

    for nombre, cantidad, total in resultados:

        respuesta.append({
            "servicio": nombre,
            "cantidad": cantidad,
            "total": float(total or 0)
        })

    return respuesta


@router.get("/range")
def reporte_por_fechas(
    desde: str,
    hasta: str,
    db=Depends(get_db)
):

    try:

        fecha_desde = datetime.strptime(
            desde,
            "%Y-%m-%d"
        )

        fecha_hasta = datetime.strptime(
            hasta,
            "%Y-%m-%d"
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail=(
                "Las fechas deben tener "
                "formato YYYY-MM-DD"
            )
        )

    if fecha_hasta < fecha_desde:

        raise HTTPException(
            status_code=400,
            detail=(
                "La fecha hasta no puede "
                "ser anterior a la fecha desde"
            )
        )

    fecha_hasta_exclusiva = (
        fecha_hasta +
        timedelta(days=1)
    )

    total = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= fecha_desde,
            Payment.date < fecha_hasta_exclusiva
        )
        .scalar() or 0
    )

    efectivo = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= fecha_desde,
            Payment.date < fecha_hasta_exclusiva,
            Payment.payment_method == "Efectivo"
        )
        .scalar() or 0
    )

    qr = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.date >= fecha_desde,
            Payment.date < fecha_hasta_exclusiva,
            Payment.payment_method == "QR"
        )
        .scalar() or 0
    )

    cantidad = (
        db.query(func.count(Payment.id))
        .filter(
            Payment.date >= fecha_desde,
            Payment.date < fecha_hasta_exclusiva
        )
        .scalar() or 0
    )

    return {
        "desde": desde,
        "hasta": hasta,
        "total": float(total),
        "efectivo": float(efectivo),
        "qr": float(qr),
        "cantidad_pagos": cantidad
    }