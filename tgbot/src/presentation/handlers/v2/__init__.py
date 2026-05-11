from .echo import (
    echo_router,
)

routers_list = [

    echo_router,  # must be last one
]

__all__ = (
    "routers_list",
)
