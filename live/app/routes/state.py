from fastapi import APIRouter

from utils import transaction

state_router = APIRouter(tags=["state"])


@transaction
@state_router.get("/probe")
async def startupProbe():
  return {"status": "ok"}


@transaction
@state_router.get("/liveness")
async def liveness():
  return {"status": "ok"}


@transaction
@state_router.get("/readiness")
async def readiness():
  return {"status": "ok"}
