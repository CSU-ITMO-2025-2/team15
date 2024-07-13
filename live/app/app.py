import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import conn
from routes.history import history_router
from routes.state import state_router
from routes.tasks import task_router
from routes.data import dataframe_router
from routes.balances import balance_router
from routes.users import user_router

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    conn()


app.include_router(user_router, prefix="/api/user")
app.include_router(balance_router, prefix="/api/balance")
app.include_router(dataframe_router, prefix="/api/df")
app.include_router(task_router, prefix="/api/task")
app.include_router(history_router, prefix="/api/history")
app.include_router(state_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
