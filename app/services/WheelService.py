import random
import logging
from typing import Dict, Any, Optional, Tuple

from app.api.models import Prize
from app.api.dao import PlayerDAO, PrizeDAO
from app.core.enums import SpinStatus


class WheelService:
    @staticmethod
    async def spin(telegram_id: int, username: str) -> Tuple[SpinStatus, Optional[Dict[str, Any]]]:
        try:
            player = await PlayerDAO.find_one_or_none(**{
                'telegram_id': telegram_id,
                'username': username
            })

            if not player:
                return SpinStatus.PLAYER_NOT_FOUND, None

            if player.has_spun:
                return SpinStatus.ALREADY_SPUN, None

            available_prizes = await PrizeDAO.get_available_prizes()

            if not available_prizes:
                return SpinStatus.NO_PRIZES, None

            selected_prize = WheelService._select_random_prize(available_prizes)

            await PlayerDAO.update(
                {
                    "has_spun": True,
                    "prize_id": selected_prize.id
                },
                telegram_id = telegram_id
            )

            await PrizeDAO.decrement_quantity(selected_prize.id)

            logging.info(f"Prize assigned: {selected_prize.name} to player {telegram_id}")

            result_data = {
                "prize": {
                    "id": selected_prize.id,
                    "name": selected_prize.name
                },
                "player": {
                    "telegram_id": player.telegram_id,
                    "username": player.username
                }
            }

            return SpinStatus.SUCCESS, result_data

        except Exception as error:
            logging.error(f"Unexpected error in WheelService.spin for {telegram_id}: {error}")

            return SpinStatus.ERROR, {"error": str(error)}


    @staticmethod
    def _select_random_prize(prizes: list[Prize]) -> Prize:
        for i in range(len(prizes) - 1, 0, -1):
            j = random.randint(0, i)
            prizes[i], prizes[j] = prizes[j], prizes[i]

        return random.choice(prizes)