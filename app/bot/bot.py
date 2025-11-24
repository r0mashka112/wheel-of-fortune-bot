from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault

from app.config import settings

bot = Bot(token = settings.BOT_TOKEN)

dp = Dispatcher()

async def set_bot_commands():
    commands = [
        BotCommand(command = 'start', description = 'Запустить бота')
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())