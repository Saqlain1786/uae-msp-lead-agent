from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agent.scheduler import start_scheduler, stop_scheduler
from app.api.routes import router
from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)
