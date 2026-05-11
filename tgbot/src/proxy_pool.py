import json
import logging
from pathlib import Path
from urllib.parse import quote

import aiohttp
from aiogram.client.session.aiohttp import AiohttpSession

logger = logging.getLogger(__name__)

PROXY_FILE = Path(__file__).resolve().parents[1] / ".proxy_cache.json"


def build_proxy_url(proxy: dict) -> str | None:
    protocol = proxy.get("protocol")
    host = proxy.get("host")
    port = proxy.get("port")

    if not protocol or not host or not port:
        return None

    username = proxy.get("username")
    password = proxy.get("password")

    if username and password:
        username = quote(username, safe="")
        password = quote(password, safe="")
        return f"{protocol}://{username}:{password}@{host}:{port}"

    return f"{protocol}://{host}:{port}"


def load_proxies() -> list[str]:
    if not PROXY_FILE.exists():
        return []

    try:
        data = json.loads(PROXY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

    return list(
        dict.fromkeys(
            filter(
                None,
                (build_proxy_url(item) for item in data if isinstance(item, dict)),
            ),
        ),
    )


async def check_proxy(proxy_url: str, bot_token: str) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/getMe"

    try:
        timeout = aiohttp.ClientTimeout(total=8)

        async with aiohttp.ClientSession(timeout=timeout) as session, session.get(url, proxy=proxy_url) as resp:
            return resp.status == 200

    except Exception:
        return False


async def find_working_proxy(bot_token: str) -> str | None:
    proxies = load_proxies()

    for proxy in proxies:
        if await check_proxy(proxy, bot_token):
            return proxy

    return None


async def create_aiogram_session(bot_token: str) -> AiohttpSession:
    proxy = await find_working_proxy(bot_token)

    if not proxy:
        raise RuntimeError("No working proxy found")

    return AiohttpSession(proxy=proxy)
