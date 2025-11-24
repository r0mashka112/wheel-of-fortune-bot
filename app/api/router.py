import asyncio
import logging

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException

from app.bot.bot import bot
from app.api.dao import PlayerDAO
from app.core.enums import SpinStatus
from app.services.WheelService import WheelService

from app.services.MessageHistoryService import message_history_service

api_router = APIRouter(prefix = '/api', tags = ['API'])


@api_router.post('/spin')
async def spin(request: Request):
    try:
        data = await request.json()
    except ValueError as error:
        logging.warning(f"Invalid JSON received: {error}")

        raise HTTPException(
            status_code = 400,
            detail = "Invalid JSON format"
        )

    telegram_id = data.get("telegram_id")
    username = data.get("username")

    if not telegram_id:
        raise HTTPException(
            status_code = 400,
            detail = "Missing required field: telegram_id"
        )

    try:
        telegram_id = int(telegram_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code = 400,
            detail = "Parameter telegram_id must be integer"
        )

    if username is not None:
        if not isinstance(username, str):
            raise HTTPException(
                status_code = 400,
                detail = "Invalid username type, must be string"
            )

        username = username.strip()

        if not username:
            username = None

    try:
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

        status, result_data = await WheelService.spin(
            telegram_id = telegram_id,
            username = username
        )

        if status == SpinStatus.SUCCESS:
            logging.info(
                f"Spin completed successfully for player: {telegram_id}"
            )

            return JSONResponse(
                status_code = 200,
                content = {
                    "status": "success",
                    "data": result_data
                }
            )
        elif status == SpinStatus.ALREADY_SPUN:
            logging.warning(f"Player {telegram_id} already spun the wheel")

            raise HTTPException(
                status_code = 400,
                detail = "You have already spun the wheel"
            )
        elif status == SpinStatus.NO_PRIZES:
            logging.warning(f"No prizes available for player {telegram_id}")

            raise HTTPException(
                status_code = 400,
                detail = "No prizes available at the moment"
            )

        elif status == SpinStatus.PLAYER_NOT_FOUND:
            logging.warning(f"Player not found: {telegram_id}")

            raise HTTPException(
                status_code = 404,
                detail = "Player not found"
            )
        elif status == SpinStatus.ERROR:
            logging.error(f"Service error for player {telegram_id}: {result_data.get('error', 'Unknown error')}")

            raise HTTPException(
                status_code = 500,
                detail = "Internal server error during spin operation"
            )

    except HTTPException:
        raise

    except Exception as error:
        logging.error(f"Database operation failed for {telegram_id}: {error}")

        raise HTTPException(
            status_code = 500,
            detail = "Failed to process player data"
        )


@api_router.post('/spin_result')
async def spin_result(request: Request):
    try:
        data = await request.json()

    except Exception:
        raise HTTPException(
            status_code = 400,
            detail = "Invalid JSON format"
        )

    telegram_id = data.get("telegram_id")
    prize = data.get("prize")

    if not telegram_id or not isinstance(telegram_id, int):
        raise HTTPException(
            status_code = 400,
            detail = "Missing or invalid required field: telegram_id"
        )

    if not prize or not isinstance(prize, str):
        raise HTTPException(
            status_code = 400,
            detail = "Missing or invalid required field: prize"
        )

    try:
        await message_history_service.delete_messages(
            chat_id = telegram_id,
            bot = bot,
            start = 1
        )

    except Exception as error:
        logging.error(f"Failed to delete messages for {telegram_id}: {error}")

    message_texts = [
        "✨ Спасибо за участие в розыгрыше Biomirix!",
        f"Ваш приз: <strong>{prize}</strong>",
        "У нас сюрприз: после выставки мы проведём ещё один розыгрыш среди всех новых подписчиков канала!",
        "Кто сможет участвовать?\nТолько те, кто останется с нами в Telegram канале Biomirix.",
        "Следите за новостями — выберем победителя на следующей неделе!"
    ]

    message_ids = []

    try:
        for text in message_texts:
            parse_mode = "HTML" if "<strong>" in text else None
            message = await bot.send_message(
                chat_id = telegram_id,
                text = text,
                parse_mode = parse_mode
            )
            message_ids.append(message.message_id)

            await asyncio.sleep(0.1)

    except Exception as error:
        logging.error(
            f"Failed to send Telegram messages to {telegram_id}: {error}"
        )

        raise HTTPException(
            status_code = 500,
            detail = "Failed to send Telegram messages"
        )

    try:
        await message_history_service.update_by(
            chat_id = telegram_id,
            message_ids = message_ids
        )

    except Exception as error:
        logging.error(
            f"Failed to update message history for {telegram_id}: {error}"
        )

    return JSONResponse(
        status_code = 200,
        content = {"detail": "ok"}
    )
