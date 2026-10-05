from pydantic import BaseModel, Field


class ClientCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        min_length=3,
        max_length=30
    )

    email: str | None = Field(
        default=None,
        max_length=150
    )


class ClientResponse(BaseModel):

    id: int
    name: str
    phone: str
    email: str | None = None

    class Config:
        from_attributes = True