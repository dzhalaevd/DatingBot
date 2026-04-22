import asyncpg
from dependency_injector.wiring import (
    Provide,
    inject,
)
from fastapi import (
    APIRouter,
    Depends,
    status,
)
from fastapi.responses import (
    JSONResponse,
)
from pydantic import (
    BaseModel,
)

from src.presentation.api.providers import (
    Container,
)
from src.shared import (
    Config,
)

healthcheck_router = APIRouter()


class Healthcheck(BaseModel):
    status: str


HEALTHCHECK_OK = Healthcheck(status="ok")
HEALTHCHECK_ERROR = Healthcheck(status="error")


# TODO: https://github.com/ets-labs/python-dependency-injector/pull/721
@healthcheck_router.get(
    "/",
    response_model=Healthcheck,
    responses={500: {"model": Healthcheck, "description": "Database unavailable"}},
    status_code=status.HTTP_200_OK,
)
@inject
async def healthcheck(
        config: Config = Depends(Provide[Container.config]),
) -> JSONResponse:
    try:
        db_conn = await asyncpg.create_pool(dsn=config.db.construct_psql_dns())
        await db_conn.execute("SELECT 1")
        await db_conn.close()
        return JSONResponse(content=HEALTHCHECK_OK.model_dump())
    except OSError:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=HEALTHCHECK_ERROR.model_dump())
