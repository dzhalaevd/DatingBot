import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

logger = structlog.stdlib.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    if hasattr(app.state, "container"):
        await app.state.container.close()


def container_factory() -> AsyncContainer:
    return make_async_container(
        SqlalchemyProvider(),
        ConfigProvider(),
        RepositoriesProvider(),
        InteractorProvider(),
        RedisProvider(),
    )


def init_services(app: FastAPI) -> None:
    init_middlewares(app)
    configure_logging()


async def start_server(app: FastAPI) -> None:
    app_config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        use_colors=True,
        log_level="debug",
        forwarded_allow_ips="*",
    )
    server = uvicorn.Server(config=app_config)
    await logger.info("Starting server")
    await server.serve()


def create_app() -> FastAPI:
    container = container_factory()
    app = FastAPI(
        title="{{ cookiecutter.project_name }}",
        version="{{ cookiecutter.version }}",
        swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
        lifespan=lifespan,
        docs_url="/",
    )

    init_services(app)
    setup_dishka(container, app)
    init_routes(app)

    return app


if __name__ == "__main__":
    try:
        application = create_app()
        with asyncio.Runner() as runner:
            runner.run(start_server(application))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down")
