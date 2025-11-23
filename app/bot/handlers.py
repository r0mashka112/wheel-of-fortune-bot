from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.config import settings
from app.core.decorators import check_subscription
from app.bot.keyboards import (
    create_mini_app_keyboard,
    create_subscribe_keyboard
)

from app.services.MessageHistoryService import message_history_service

BASE_MESSAGE = (
    'Добро пожаловать в бот розыгрыша от <strong>Biomirix!</strong> '
    'Победители будут определены мгновенно — удачи!'
)

MESSAGE_IF_SUBSCRIBED = (
    'Нажмите на кнопку ниже, чтобы запустить колесо фортуны'
)

MESSAGE_IF_NOT_SUBSCRIBED = (
    'Для <strong>участия</strong> в розыгрыше нужно '
    '<strong>подписаться</strong> на наш Telegram канал'
)

MESSAGE_IF_NOT_UNDERSTAND = 'К сожалению, не понял тебя'

router_handlers = Router()


@router_handlers.message(Command('start'))
@check_subscription(chat_id = settings.CHAT_ID)
async def handle_start(message: Message, is_subscribed, **kwargs):
    await message_history_service.update_by(
        chat_id = message.chat.id,
        message_ids = [message.message_id]
    )

    await message_history_service.delete_messages(
        chat_id = message.from_user.id,
        bot = kwargs.get('bot'),
        end = -2
    )

    if is_subscribed:
        msg_base = await message.answer(
            text = BASE_MESSAGE,
            parse_mode = 'HTML'
        )

        msg_secondary = await message.answer(
            text = MESSAGE_IF_SUBSCRIBED,
            reply_markup = create_mini_app_keyboard()
        )

        await message_history_service.update_by(
            chat_id = message.from_user.id,
            message_ids = [
                msg_base.message_id,
                msg_secondary.message_id
            ]
        )
    else:
        msg_secondary = await message.answer(
            text = MESSAGE_IF_NOT_SUBSCRIBED,
            reply_markup = create_subscribe_keyboard(),
            parse_mode = 'HTML'
        )

        await message_history_service.update_by(
            chat_id = message.from_user.id,
            message_ids = [
                msg_secondary.message_id
            ]
        )


@router_handlers.callback_query(F.data == 'start_draw')
@check_subscription(chat_id = settings.CHAT_ID)
async def handle_callback_query(callback_query: CallbackQuery, is_subscribed, **kwargs):
    await callback_query.answer()

    if is_subscribed:
        await message_history_service.delete_messages(
            chat_id = callback_query.from_user.id,
            bot = kwargs.get('bot'),
            start = 1
        )

        msg_base = await callback_query.message.answer(
            text = BASE_MESSAGE,
            parse_mode = 'HTML'
        )

        msg_secondary = await callback_query.message.answer(
            text = MESSAGE_IF_SUBSCRIBED,
            reply_markup = create_mini_app_keyboard()
        )

        await message_history_service.update_by(
            chat_id = callback_query.from_user.id,
            message_ids = [
                msg_base.message_id,
                msg_secondary.message_id
            ]
        )
    else:
        msg = await callback_query.message.answer(
            text = MESSAGE_IF_NOT_SUBSCRIBED,
            parse_mode = 'HTML'
        )

        await message_history_service.update_by(
            chat_id = callback_query.from_user.id,
            message_ids = [
                msg.message_id
            ]
        )


@router_handlers.message()
async def handle_text(message: Message):
    msg = await message.answer(
        text = MESSAGE_IF_NOT_UNDERSTAND
    )

    await message_history_service.update_by(
        chat_id = message.from_user.id,
        message_ids = [
            message.message_id,
            msg.message_id
        ]
    )
