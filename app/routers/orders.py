from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/", response_model=schemas.OrderPublic, status_code=status.HTTP_201_CREATED
)
def create_order(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    cart_items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == current_user.id)
        .all()
    )
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_cents = 0
    order_items = []
    for item in cart_items:
        product = item.product
        if not product.is_active:
            raise HTTPException(status_code=400, detail="Inactive product in cart")
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400, detail=f"Insufficient stock for {product.name}"
            )

        total_cents += product.price_cents * item.quantity
        order_items.append(
            models.OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price_cents=product.price_cents,
            )
        )
        product.stock -= item.quantity

    order = models.Order(user_id=current_user.id, total_cents=total_cents)
    order.items = order_items

    db.add(order)
    for item in cart_items:
        db.delete(item)

    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=list[schemas.OrderPublic])
def list_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )


@router.get("/{order_id}", response_model=schemas.OrderPublic)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    order = (
        db.query(models.Order)
        .filter(models.Order.id == order_id, models.Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
