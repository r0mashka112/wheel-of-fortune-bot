from app.config import settings
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, WebAppInfo


def create_mini_app_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(
        text = 'Запустить колесо фортуны',
        web_app = WebAppInfo(url = settings.BASE_SITE)
    ).as_markup(resize_keyboard = True)


def create_subscribe_keyboard() -> InlineKeyboardMarkup:
    return (InlineKeyboardBuilder()
        .button(
            text = 'Подписаться',
            url = 'https://t.me/biomirix'
        ).button(
            text = 'Начать розыгрыш',
            callback_data = 'start_draw'
        )
        .adjust(1)
        .as_markup()
    )