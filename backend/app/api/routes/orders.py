from fastapi import APIRouter, Query

from app.schemas.loyalty import CreateOrderRequest, OperationResult, Order, RefundOrderRequest
from app.services.loyalty_service import LoyaltyService

router = APIRouter()
service = LoyaltyService()


@router.get("", response_model=list[Order])
def list_orders(member_id: int | None = Query(default=None)) -> list[dict]:
    return service.list_orders(member_id)


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int) -> dict:
    return service.get_order(order_id)


@router.post("", response_model=OperationResult)
def create_order(payload: CreateOrderRequest) -> dict:
    return service.create_order(
        payload.member_id,
        payload.original_amount,
        payload.rule_id,
        payload.note,
    )


@router.post("/{order_id}/refund", response_model=OperationResult)
def refund_order(order_id: int, payload: RefundOrderRequest | None = None) -> dict:
    note = payload.note if payload else None
    return service.refund_order(order_id, note)
