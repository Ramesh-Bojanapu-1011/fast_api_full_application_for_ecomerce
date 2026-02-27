from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/cart", tags=["cart"])


def _cart_subtotal(items: list[models.CartItem]) -> int:
    return sum(item.product.price_cents * item.quantity for item in items)


@router.get("/", response_model=schemas.CartPublic)
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == current_user.id)
        .all()
    )
    return {"items": items, "subtotal_cents": _cart_subtotal(items)}


@router.post(
    "/items", response_model=schemas.CartPublic, status_code=status.HTTP_201_CREATED
)
def add_item(
    payload: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    product = (
        db.query(models.Product).filter(models.Product.id == payload.product_id).first()
    )
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not available")

    item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.user_id == current_user.id,
            models.CartItem.product_id == payload.product_id,
        )
        .first()
    )
    if item:
        item.quantity += payload.quantity
    else:
        item = models.CartItem(
            user_id=current_user.id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        db.add(item)

    db.commit()
    db.refresh(item)

    items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == current_user.id)
        .all()
    )
    return {"items": items, "subtotal_cents": _cart_subtotal(items)}


@router.patch("/items/{item_id}", response_model=schemas.CartPublic)
def update_item(
    item_id: int,
    payload: schemas.CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.id == item_id, models.CartItem.user_id == current_user.id
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if payload.quantity == 0:
        db.delete(item)
    else:
        item.quantity = payload.quantity

    db.commit()

    items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == current_user.id)
        .all()
    )
    return {"items": items, "subtotal_cents": _cart_subtotal(items)}


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.id == item_id, models.CartItem.user_id == current_user.id
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()
    return None
