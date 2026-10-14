from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, conint, constr


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(
        min_length=8, max_length=72
    )  # pyright: ignore[reportInvalidTypeForm]
    role: Literal["customer", "store"] = "customer"


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: constr(min_length=2, max_length=255)  # pyright: ignore[reportInvalidTypeForm]
    description: str | None = None
    price_cents: conint(ge=0)  # type: ignore
    stock: conint(ge=0) = 0  # pyright: ignore[reportInvalidTypeForm]


class ProductUpdate(BaseModel):
    name: constr(min_length=2, max_length=255) | None = ( # pyright: ignore[reportInvalidTypeForm]
        None  # pyright: ignore[reportInvalidTypeForm]
    )
    description: str | None = None
    price_cents: conint(ge=0) | None = None  # pyright: ignore[reportInvalidTypeForm]
    stock: conint(ge=0) | None = None  # pyright: ignore[reportInvalidTypeForm]
    is_active: bool | None = None


class ProductPublic(BaseModel):
    id: int
    name: str
    description: str | None
    price_cents: int
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartItemCreate(BaseModel):
    product_id: int
    quantity: conint(ge=1)  # pyright: ignore[reportInvalidTypeForm]


class CartItemUpdate(BaseModel):
    quantity: conint(ge=0)  # pyright: ignore[reportInvalidTypeForm]


class CartItemPublic(BaseModel):
    id: int
    product: ProductPublic
    quantity: int

    class Config:
        from_attributes = True


class CartPublic(BaseModel):
    items: list[CartItemPublic]
    subtotal_cents: int


class OrderItemPublic(BaseModel):
    id: int
    product: ProductPublic
    quantity: int
    unit_price_cents: int

    class Config:
        from_attributes = True


class OrderPublic(BaseModel):
    id: int
    total_cents: int
    status: str
    created_at: datetime
    items: list[OrderItemPublic]


class UsersByRole(BaseModel):
    stores: list[UserPublic]
    customers: list[UserPublic]

    class Config:
        from_attributes = True
