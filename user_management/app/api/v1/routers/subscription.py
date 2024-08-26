from fastapi import APIRouter, HTTPException
from app.api.v1.services.subscription_service import create_subscription, delete_subscription

router = APIRouter()

@router.post("/subscribe/{user_id}/{stock_code}")
async def subscribe(user_id: int, stock_code: str):
    """Subscribe a user to a stock."""
    await create_subscription(user_id, stock_code)
    return {"status": "subscribed", "stock_code": stock_code}

@router.post("/unsubscribe/{user_id}/{stock_code}")
async def unsubscribe(user_id: int, stock_code: str):
    """Unsubscribe a user from a stock."""
    await delete_subscription(user_id, stock_code)
    return {"status": "unsubscribed", "stock_code": stock_code}
