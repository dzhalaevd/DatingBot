import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

import aiohttp
from aiogram.client.session.aiohttp import AiohttpSession

logger = logging.getLogger(__name__)

PROXY_SOURCES: dict[str, str] = {
    "http": (
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/"
        "proxies/protocols/http/data.json"
    ),
    "socks5": (
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/"
        "proxies/protocols/socks5/data.json"
    ),
}

PROXY_CACHE_FILE = Path(".proxy_cache.json")
PROXY_CACHE_TTL_SECONDS = 60 * 30  # 30 минут


def load_cached_proxy() -> str | None:
    if not PROXY_CACHE_FILE.exists():
        logger.debug("Proxy cache file does not exist")
        return None

    try:
        payload = json.loads(PROXY_CACHE_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to read proxy cache: %s", exc)
        return None

    proxy = payload.get("proxy")
    cached_at = payload.get("cached_at")

    if not isinstance(proxy, str) or not proxy:
        logger.debug("Proxy cache is invalid: missing proxy")
        return None

    if not isinstance(cached_at, (int, float)):
        logger.debug("Proxy cache is invalid: missing cached_at")
        return None

    age = time.time() - float(cached_at)
    if age > PROXY_CACHE_TTL_SECONDS:
        logger.info("Cached proxy expired: %s", proxy)
        clear_cached_proxy()
        return None

    logger.info("Using cached proxy candidate: %s", proxy)
    return proxy


def save_cached_proxy(proxy_url: str) -> None:
    payload = {
        "proxy": proxy_url,
        "cached_at": time.time(),
    }

    try:
        PROXY_CACHE_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Saved working proxy to cache: %s", proxy_url)
    except Exception as exc:
        logger.warning("Failed to save proxy cache: %s", exc)


def clear_cached_proxy() -> None:
    try:
        PROXY_CACHE_FILE.unlink(missing_ok=True)
        logger.debug("Proxy cache cleared")
    except Exception as exc:
        logger.warning("Failed to clear proxy cache: %s", exc)


async def fetch_proxy_candidates(
        protocol: str,
        timeout: float = 10.0,
) -> list[str]:
    url = PROXY_SOURCES[protocol]
    logger.info("Fetching %s proxy list from %s", protocol.upper(), url)

    client_timeout = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(timeout=client_timeout) as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            data: Any = await resp.json(content_type=None)

    proxies: list[str] = []

    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue

            proxy = item.get("proxy")
            item_protocol = item.get("protocol")
            score = item.get("score", 0)

            if (
                    isinstance(proxy, str)
                    and item_protocol == protocol
                    and proxy.startswith(f"{protocol}://")
                    and isinstance(score, (int, float))
                    and score >= 1
            ):
                proxies.append(proxy)

    unique_proxies = list(dict.fromkeys(proxies))
    logger.info(
        "Fetched %s %s proxy candidates (%s unique)",
        len(proxies),
        protocol.upper(),
        len(unique_proxies),
    )

    return unique_proxies


async def fetch_all_proxy_candidates(timeout: float = 10.0) -> list[str]:
    http_task = asyncio.create_task(fetch_proxy_candidates("http", timeout=timeout))
    socks5_task = asyncio.create_task(fetch_proxy_candidates("socks5", timeout=timeout))

    http_candidates, socks5_candidates = await asyncio.gather(
        http_task,
        socks5_task,
        return_exceptions=False,
    )

    combined = socks5_candidates + http_candidates
    unique_combined = list(dict.fromkeys(combined))

    logger.info(
        "Total combined proxy candidates: %s (%s HTTP + %s SOCKS5)",
        len(unique_combined),
        len(http_candidates),
        len(socks5_candidates),
    )

    return unique_combined


async def check_proxy_telegram(
        proxy_url: str,
        bot_token: str,
        timeout: float = 8.0,
) -> bool:
    telegram_url = f"https://api.telegram.org/bot{bot_token}/getMe"
    client_timeout = aiohttp.ClientTimeout(total=timeout)

    logger.debug("Checking proxy: %s", proxy_url)

    try:
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.get(telegram_url, proxy=proxy_url) as resp:
                if resp.status != 200:
                    logger.debug(
                        "Proxy %s failed with HTTP status %s",
                        proxy_url,
                        resp.status,
                    )
                    return False

                data = await resp.json(content_type=None)
                ok = bool(data.get("ok") is True)

                if ok:
                    logger.info("Working proxy found: %s", proxy_url)
                else:
                    logger.debug(
                        "Proxy %s returned non-ok Telegram response",
                        proxy_url,
                    )

                return ok

    except Exception as exc:
        logger.debug("Proxy %s failed: %s", proxy_url, exc)
        return False


async def pick_first_working_proxy(
        candidates: list[str],
        bot_token: str,
        concurrency: int = 20,
) -> str | None:
    semaphore = asyncio.Semaphore(concurrency)

    async def wrapped_check(proxy_url: str) -> str | None:
        async with semaphore:
            ok = await check_proxy_telegram(proxy_url, bot_token)
            return proxy_url if ok else None

    tasks = [asyncio.create_task(wrapped_check(proxy)) for proxy in candidates]

    try:
        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result:
                logger.info("Selected first working proxy: %s", result)

                for task in tasks:
                    if not task.done():
                        task.cancel()

                await asyncio.gather(*tasks, return_exceptions=True)
                return result
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    logger.warning("No working proxy found among checked candidates")
    return None


async def find_working_proxy(
        bot_token: str,
        limit: int = 200,
        concurrency: int = 20,
) -> str | None:
    cached_proxy = load_cached_proxy()
    if cached_proxy:
        logger.info("Validating cached proxy")
        if await check_proxy_telegram(cached_proxy, bot_token):
            logger.info("Cached proxy is still working")
            return cached_proxy

        logger.warning("Cached proxy is dead, removing from cache")
        clear_cached_proxy()

    candidates = await fetch_all_proxy_candidates()
    candidates = candidates[:limit]

    logger.info("Checking up to %s proxy candidates", len(candidates))

    working_proxy = await pick_first_working_proxy(
        candidates=candidates,
        bot_token=bot_token,
        concurrency=concurrency,
    )

    if working_proxy:
        save_cached_proxy(working_proxy)

    return working_proxy


async def create_aiogram_session(bot_token: str) -> AiohttpSession:
    proxy_url = await find_working_proxy(bot_token=bot_token)

    if proxy_url is None:
        raise RuntimeError("No working HTTP/SOCKS5 proxy found")

    logger.info("Creating Aiogram session with proxy: %s", proxy_url)
    return AiohttpSession(proxy=proxy_url)
