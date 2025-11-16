from app.dao.base import BaseDAO
from app.api.models import Player, Prize

class PlayerDAO(BaseDAO):
    model = Player

class PrizeDAO(BaseDAO):
    model = Prize

    @classmethod
    async def get_available_prizes(cls) -> list[Prize]:
        all_prizes = await cls.find_all()

        return list(filter(
            lambda prize: prize.quantity > 0, all_prizes
        ))


    @classmethod
    async def decrement_quantity(cls, prize_id: int) -> None:
        prize = await cls.find_one_or_none(
            **{'id': prize_id}
        )

        if prize and prize.quantity > 0:
            await cls.update(
                {'quantity': prize.quantity - 1},
                id = prize.id
            )