from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Literal


class PaymentCreate(BaseModel):
    client_id: int | None = Field(
        default=None,
        gt=0
    )

    service_id: int = Field(
        gt=0
    )

    amount: Decimal = Field(
        gt=0
    )

    payment_method: Literal[
        "Efectivo",
        "QR"
    ]


class PaymentResponse(BaseModel):
    id: int
    cliente: str
    servicio: str
    monto: Decimal
    metodo_pago: str
    fecha: datetime