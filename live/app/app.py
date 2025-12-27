import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from database.database import conn, init_db, db_session
from routes.balances import balance_router
from routes.data import dataframe_router
from routes.history import history_router
from routes.state import state_router
from routes.tasks import task_router
from routes.users import user_router

app = FastAPI()

instrumentator = Instrumentator().instrument(app)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
  conn()
  instrumentator.expose(app)
  await init_db()
  print("Metrics exposed!")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
  try:
    return await call_next(request)
  except Exception as e:
    db_session.rollback()
    raise e
  finally:
    db_session.remove()


app.include_router(user_router, prefix="/api/user")
app.include_router(balance_router, prefix="/api/balance")
app.include_router(dataframe_router, prefix="/api/df")
app.include_router(task_router, prefix="/api/task")
app.include_router(history_router, prefix="/api/history")
app.include_router(state_router, prefix="/api")

if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=8081, reload=True)
