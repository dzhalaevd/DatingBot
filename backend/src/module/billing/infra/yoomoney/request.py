from aiohttp import (
    ClientResponse,
    ClientSession,
)
from aiohttp.client_exceptions import (
    ContentTypeError,
)

from utils.yoomoney.exceptions import (
    BadResponse,
    UnresolvedRequestMethod,
)

ALLOWED_METHODS = ("post", "get")


async def send_request(
        url: str, method: str = "post", response_without_data: bool = False, **kwargs
) -> (ClientResponse, dict | None):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if add_headers := kwargs.pop("headers", {}):
        headers |= add_headers

    method = method.lower().strip()
    await check_method(method)

    async with ClientSession() as session:
        async with getattr(session, method)(url, headers=headers, **kwargs) as response:
            await post_handle_response(response)

            if response_without_data:
                return response

            return response, await response.json()


async def check_method(method: str):
    if method not in ALLOWED_METHODS:
        raise UnresolvedRequestMethod


async def post_handle_response(response: ClientResponse):
    try:
        response_data = await response.json()
        if isinstance(response_data, dict) and response_data.get("error"):
            raise BadResponse(
                f"error — {response_data.get('error')}, response is {response}"
            )

    except ContentTypeError:
        pass

    if response.status >= 400:
        raise BadResponse(response)
