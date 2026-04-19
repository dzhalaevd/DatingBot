import asyncio

from data.config import (
    load_config,
)
from utils.yoomoney import (
    authorize_app,
)


async def main():
    await authorize_app(
        client_id=load_config().misc.client_id,
        redirect_uri=load_config().misc.redirect_url,
        app_permissions=[
            "account-info",
            "operation-history",
            "operation-details",
            "incoming-transfers",
            "payment-p2p",
            "payment-shop",
        ],
    )


if __name__ == "__main__":
    asyncio.run(main())
