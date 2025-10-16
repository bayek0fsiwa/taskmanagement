import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlmodel import select

from configs.db import SessionDep, create_db_and_tables
from taskmanagement.controllers import router
from taskmanagement.models import Task
from utils.loger import LoggerSetup


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.logger_setup_instance = LoggerSetup(logger_name=__name__)
    app.state.logger = logging.getLogger(__name__)
    logging.getLogger("uvicorn.access").propagate = False

    app.state.logger.info("App starting")
    app.state.logger.info("Initializing database and tables.")
    try:
        await create_db_and_tables()
        app.state.logger.info("Database initialized.")
    except Exception:
        app.state.logger.error(
            "Error initializing database. The application will not start.",
            exc_info=True,
        )
        raise
    yield
    app.state.logger.info("App shutting down. Waiting for logs to be processed...")
    logger_setup = getattr(app.state, "logger_setup_instance", None)
    if logger_setup is not None:
        listener = getattr(logger_setup, "listener", None)
        if listener is not None:
            try:
                listener.stop()
            except Exception:
                app.state.logger.exception("Failed to stop logger listener cleanly.")
    app.state.logger.info("App stopped")


app = FastAPI(lifespan=lifespan)
app.include_router(router=router)


async def db_is_healthy(session: SessionDep) -> bool:
    try:
        result = await session.exec(select(Task.id).limit(1))
        _ = result.first()
        return True
    except Exception:
        return False


@app.get("/", status_code=status.HTTP_200_OK)
def app_health_check():
    logger = getattr(app.state, "logger", logging.getLogger("app"))
    logger.info("Health check endpoint accessed.", extra={"path": "/"})
    return {"status": "Online"}


@app.get("/db-health", status_code=status.HTTP_200_OK)
async def db_health_check(session: SessionDep):
    logger = getattr(app.state, "logger", logging.getLogger("app"))
    logger.info("DB health check endpoint accessed.", extra={"path": "/"})
    ok = await db_is_healthy(session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unreachable",
        )
    return {"status": "ok"}
