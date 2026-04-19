from fastapi import APIRouter, Request, HTTPException
from aiogram.types import Update

router = APIRouter()


@router.get("/health", summary="Healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/webhook", summary="Telegram webhook")
async def telegram_webhook(request: Request) -> dict[str, bool]:
    bot = request.app.state.bot
    dp = request.app.state.dp
    config = request.app.state.config

    secret_token = getattr(config.tg_bot, "secret_token", None)
    if secret_token:
        incoming_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if incoming_secret != secret_token:
            raise HTTPException(status_code=403, detail="Invalid secret token")

    try:
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid update: {exc}") from exc

    return {"ok": True}
