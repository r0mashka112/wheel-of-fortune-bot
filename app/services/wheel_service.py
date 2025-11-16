import random
from app.api.models import Prize
from app.api.dao import PlayerDAO, PrizeDAO


class WheelService:
    @staticmethod
    async def spin(telegram_id: int, username: str) -> dict:
        player = await PlayerDAO.find_one_or_none(**{
            'telegram_id': telegram_id,
            'username': username
        })

        if not player:
            raise ValueError("Player not found")

        if player.has_spun:
            raise ValueError("You have already spun the wheel")

        available_prizes = await PrizeDAO.get_available_prizes()

        if not available_prizes:
            raise ValueError("No prizes available")

        random_prize = WheelService._select_random_prize(available_prizes)

        await PlayerDAO.update(
            {
                "has_spun": True,
                "prize_id": random_prize.id
            },
            telegram_id = telegram_id
        )

        await PrizeDAO.decrement_quantity(random_prize.id)

        return {
            "status": "success",
            "prize": {
                "id": random_prize.id,
                "name": random_prize.name
            },
            "player": player
        }


    @staticmethod
    def _select_random_prize(prizes: list[Prize]) -> Prize:
        for i in range(len(prizes) - 1, 0, -1):
            j = random.randint(0, i)
            prizes[i], prizes[j] = prizes[j], prizes[i]

        return random.choice(prizes)