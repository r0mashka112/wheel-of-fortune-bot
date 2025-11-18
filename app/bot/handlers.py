from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.config import settings
from app.core.decorators import check_subscription
from app.bot.keyboards import (
    create_mini_app_keyboard,
    create_subscribe_keyboard
)

BASE_MESSAGE = (
    'Добро пожаловать в бот розыгрыша от <strong>Biomirix!</strong> '
    'Победители будут определены мгновенно — удачи!'
)

MESSAGE_IF_SUBSCRIBED = (
    'Нажмите на кнопку ниже, чтобы запустить колесо фортуны'
)

MESSAGE_IF_NOT_SUBSCRIBED = (
    'Для запуска колеса фортуны нужно подписаться на наш канал'
)

router_handlers = Router()

@router_handlers.message(Command('start'))
@check_subscription(chat_id = settings.CHAT_ID)
async def handle_start(message: Message, is_subscribed) -> None:
    if is_subscribed:
        await message.answer(
            text = BASE_MESSAGE,
            parse_mode = 'HTML'
        )

        await message.answer(
            text = MESSAGE_IF_SUBSCRIBED,
            reply_markup = create_mini_app_keyboard()
        )
    else:
        await message.answer(
            text = MESSAGE_IF_NOT_SUBSCRIBED,
            reply_markup = create_subscribe_keyboard()
        )


@router_handlers.callback_query(F.data == 'check_subscribe')
@check_subscription(chat_id = settings.CHAT_ID)
async def handle_callback_query(callback_query: CallbackQuery, is_subscribed):
    await callback_query.answer()

    if is_subscribed:
        await callback_query.message.answer(
            text = BASE_MESSAGE,
            parse_mode = 'HTML'
        )

        await callback_query.message.answer(
            text = MESSAGE_IF_SUBSCRIBED,
            reply_markup = create_mini_app_keyboard()
        )
    else:
        await callback_query.message.answer(
            text = MESSAGE_IF_NOT_SUBSCRIBED
        )