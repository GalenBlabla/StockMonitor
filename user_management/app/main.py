from fastapi import FastAPI
from app.core.startup import lifespan
from app.api.v1.routers import subscription,user

app = FastAPI(lifespan=lifespan)

app.include_router(subscription.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")