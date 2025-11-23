import logging

from aiogram import Bot
from app.database import redis


class MessageHistoryService:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def update_by(self, chat_id: int, message_ids: list[int]):
        for message_id in message_ids:
            await self.redis.rpush(f'chat_id:{chat_id}', message_id)
            await self.redis.expire(f'chat_id:{chat_id}', 3600 * 48)

    async def _clear_by(self, chat_id: int, message_id: int):
        await self.redis.lrem(f'chat_id:{chat_id}', 1, message_id)

    async def delete_messages(
        self,
        chat_id: int,
        bot: Bot,
        start: int = None,
        end: int = None
    ):
        if start is None and end is None:
            messages = await self.redis.lrange(f'chat_id:{chat_id}', 0, -1)
        elif start is not None and end is None:
            messages = await self.redis.lrange(f'chat_id:{chat_id}', start, -1)
        elif start is None and end is not None:
            messages = await self.redis.lrange(f'chat_id:{chat_id}', 0, end)
        else:
            messages = await self.redis.lrange(f'chat_id:{chat_id}', start, end)

        for message_id in messages:
            try:
                await bot.delete_message(chat_id = chat_id, message_id = message_id)
                await self._clear_by(chat_id = chat_id, message_id = message_id)
            except Exception as error:
                logging.error(f"Can't delete message {message_id}", exc_info = error)


message_history_service = MessageHistoryService(redis_client = redis)