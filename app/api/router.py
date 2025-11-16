from fastapi.requests import Request
from fastapi import APIRouter, HTTPException


from app.bot.bot import bot
from app.api.dao import PlayerDAO
from app.services.wheel_service import WheelService

api_router = APIRouter(prefix = '/api', tags = ['API'])


@api_router.post('/spin')
async def spin(request: Request):
    data = await request.json()

    telegram_id = data.get("telegram_id")
    username = data.get("username")

    if not telegram_id:
        raise HTTPException(400, "Telegram ID required")

    player = await PlayerDAO.find_one_or_none(
        telegram_id = telegram_id
    )

    if not player:
        new_player = await PlayerDAO.create(
            telegram_id = telegram_id,
            username = username
        )
    elif player.username != username:
        await PlayerDAO.update(
            {"username": username},
            telegram_id = telegram_id
        )

    try:
        result = await WheelService.spin(
            telegram_id = telegram_id,
            username = username
        )

        return result
    except ValueError as error:
        raise HTTPException(400, str(error))
    except Exception:
        raise HTTPException


@api_router.post('/spin_result')
async def spin_result(request: Request):
    data = await request.json()

    telegram_id = data.get("telegram_id")
    prize = data.get("prize")

    if not telegram_id or not prize:
        return {"status": "error", "message": "Invalid data"}

    try:
        await bot.send_message(
            chat_id = telegram_id,
            text = "✨ Спасибо за участие в розыгрыше Biomirix!",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id = telegram_id,
            text = f"Ваш приз: <strong>{prize}</strong>",
            parse_mode = "HTML"
        )

        await bot.send_message(
            chat_id = telegram_id,
            text = "У нас сюрприз: после выставки мы проведём ещё один розыгрыш среди всех новых подписчиков канала!"
        )

        await bot.send_message(
            chat_id = telegram_id,
            text = (
                "Кто сможет участвовать?\n"
                "Только те, кто останется с нами в Telegram канале Biomirix."
            )
        )

        await bot.send_message(
            chat_id = telegram_id,
            text = "Следите за новостями — выберем победителя на следующей неделе!"
        )
    except Exception as error:
        return {"status": "error", "message": str(error)}

    return {"status": "ok"}
