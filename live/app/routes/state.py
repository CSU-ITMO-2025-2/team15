from fastapi import APIRouter

state_router = APIRouter(tags=["state"])


@state_router.get("/liveness")
async def liveness():
    return {"status": "ok"}


@state_router.get("/readiness")
async def readiness():
    return {"status": "ok"}
