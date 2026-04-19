import asyncio

import uvicorn

from tgbot.infra.webhook.app import create_app


async def main() -> None:
    app = create_app()

    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )

    server = uvicorn.Server(config)

    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
