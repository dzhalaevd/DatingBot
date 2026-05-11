from fastapi import (
    FastAPI,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette_exporter import (
    PrometheusMiddleware,
    handle_metrics,
)

from .api import (
    auth_router,
    healthcheck_router,
    role_router,
    user_router,
    profile_router,
    photo_router,
)
from .api.middlewares import (
    logging_middleware,
)
from .api.providers import (
    Container,
)


def setup_routes(app: FastAPI) -> None:
    prefix: str = "/api/v1"
    app.include_router(
        router=auth_router, prefix=f"{prefix}/auth", tags=["Authorization"],
    )
    app.include_router(
        router=user_router, prefix=f"{prefix}/users", tags=["User"],
    )
    app.include_router(
        router=role_router, prefix=f"{prefix}/roles", tags=["Role"],
    )
    app.include_router(
        router=healthcheck_router, prefix=f"{prefix}/healthcheck", tags=["Healthcheck"],
    )
    app.include_router(
        router=profile_router, prefix=f"{prefix}/profiles", tags=["Profile"]
    )
    app.include_router(
        router=photo_router, prefix=f"{prefix}/photos", tags=["Photo"]
    )
    app.add_route("/metrics", handle_metrics)


# noinspection PyTypeChecker
def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        BaseHTTPMiddleware, dispatch=logging_middleware,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )
    app.add_middleware(PrometheusMiddleware)


__all__ = (
    "setup_middlewares",
    "setup_routes",
    "Container"
)
