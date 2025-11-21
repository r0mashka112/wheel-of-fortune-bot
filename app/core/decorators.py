import logging
import traceback
from functools import wraps
from typing import Callable
from fastapi import HTTPException

from aiogram import Bot
from aiogram.types import Message

from sqlalchemy.exc import (
    NoResultFound,
    IntegrityError,
    SQLAlchemyError
)


def handle_db_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger("api")

        try:
            return await func(*args, **kwargs)
        except IntegrityError as error:
            logger.error(
                f"IntegrityError in {func.__name__}: {str(error)}\n"
                f"Traceback: {traceback.format_exc()}"
            )

            raise HTTPException(
                status_code = 400,
                detail = "User data conflict"
            )

        except ValueError as error:
            logger.warning(f"ValueError in {func.__name__}: {str(error)}")

            raise HTTPException(
                status_code = 400,
                detail = str(error)
            )

        except NoResultFound as error:
            logger.warning(
                f"NoResultFound in {func.__name__}\n"
                f"Args: {args}, Kwargs: {kwargs}\n"
                f"Error: {str(error)}"
            )

            raise HTTPException(
                status_code = 404,
                detail = "User not found"
            )

        except SQLAlchemyError as error:
            logger.error(
                f"SQLAlchemyError in {func.__name__}: {str(error)}\n"
                f"Traceback: {traceback.format_exc()}"
            )

            raise HTTPException(
                status_code = 500,
                detail = "Database operation failed"
            )

        except Exception as error:
            logger.critical(
                f"Unexpected error in {func.__name__}: {str(error)}\n"
                f"Traceback: {traceback.format_exc()}"
            )

            raise HTTPException(
                status_code = 500,
                detail = "Internal server error"
            )

    return wrapper


def check_subscription(chat_id: int):
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(message: Message, *args, **kwargs):
            logger = logging.getLogger("decorator")
            bot: Bot = message.bot

            try:
                chat_member = await bot.get_chat_member(
                    chat_id = chat_id,
                    user_id = message.from_user.id
                )

                is_subscribed = chat_member.status in [
                    'member', 'administrator', 'creator'
                ]
            except Exception as error:
                logger.error(
                    f"Unexpected error in {handler.__name__}: {str(error)}\n"
                    f"Traceback: {traceback.format_exc()}"
                )
                is_subscribed = False

            return await handler(message, is_subscribed, *args, **kwargs)
        return wrapper
    return decorator