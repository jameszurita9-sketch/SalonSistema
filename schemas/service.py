from pydantic import BaseModel, Field
from decimal import Decimal


class ServiceCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    price: Decimal = Field(
        gt=0,
        decimal_places=2,
        max_digits=10
    )