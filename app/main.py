import logging
import uvicorn

from sqladmin import Admin

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from aiogram.types import Update

from app.bot.bot import bot, dp
from app.config import settings
from app.database import engine
from app.api.router import api_router
from app.pages.router import router_pages
from app.bot.handlers import router_handlers
from app.pages.admin import PlayerAdmin, PrizeAdmin

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting bot setup...")

    dp.include_router(router_handlers)

    await bot.set_webhook(
        url = settings.WEBHOOK_URL,
        allowed_updates = dp.resolve_used_update_types(),
        drop_pending_updates = True
    )

    logging.info(f"Webhook set to {settings.WEBHOOK_URL}")
    yield

    logging.info("Shutting down bot...")
    await bot.delete_webhook()
    await bot.session.close()
    logging.info("Webhook deleted")


app = FastAPI(lifespan = lifespan)

admin = Admin(app, engine)

admin.add_view(PlayerAdmin)
admin.add_view(PrizeAdmin)

app.mount(
    '/static',
    StaticFiles(directory = 'app/static', html = True),
    name = 'static'
)

app.include_router(router_pages)
app.include_router(api_router)

@app.post('/webhook')
async def webhook(request: Request) -> None:
    logging.info("Received webhook request")

    update = Update.model_validate(
        await request.json(),
        context = {'bot': bot}
    )

    await dp.feed_update(bot, update)

    logging.info("Update processed")


if __name__ == '__main__':
    uvicorn.run('app.main:app', host = '0.0.0.0', port = 8000)