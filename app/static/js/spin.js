export const spinWheel = async (player) => {
    const wheel = document.querySelector(".wheel__sectors-container");
    const spinBtn = document.querySelector(".spin-btn");

    if (!wheel || !spinBtn) {
        return { error: 'UI элементы не найдены' };
    }

    spinBtn.disabled = true;

    const controller = new AbortController();
    const FETCH_TIMEOUT = 10000;
    const timeoutId = setTimeout(
        () => controller.abort(),
        FETCH_TIMEOUT
    );

    try {
        const response = await fetch('/api/spin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                telegram_id: player.telegram_id,
                username: player.username
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId)

        if (!response.ok) {
            let detail;

            try {
                detail = (await response.json()).detail;
            } catch {
                detail = `HTTP Status: ${response.status}`;
            }

            const errorMessages = {
                "You have already spun the wheel": "Вы уже вращали колесо!",
                "No prizes available at the moment": "Розыгрыш завершился. Все призы закончились",
                "Player not found": "Пользователь не найден",
                "Invalid JSON format": "Ошибка формата данных",
                "Missing required field: telegram_id": "Отсутствует идентификатор пользователя"
            };

            return {
                error: errorMessages[detail] || `Ошибка: ${detail}`
            };
        }

        const spinResult = await response.json();

        if (!spinResult.data?.prize) {
            return {
                error: 'Неверный формат ответа от сервера'
            };
        }

        return new Promise((resolve, reject) => {
            try {
                const rotation = Math.ceil(Math.random() * 7200);
                wheel.style.transform = `rotate(${rotation}deg)`;

                const onTransitionEnd = () => {
                    wheel.removeEventListener('transitionend', onTransitionEnd);
                    spinBtn.disabled = false;

                    resolve({
                        success: {
                            telegram_id: player.telegram_id,
                            username: player.username,
                            prize_id: spinResult.data.prize.id,
                            prize: spinResult.data.prize.name
                        }
                    });
                };

                wheel.addEventListener(
                    'transitionend',
                    onTransitionEnd,
                    { once: true }
                );
            } catch (animationError) {
                spinBtn.disabled = false;
                reject({ error: 'Ошибка при запуске анимации: ' + animationError });
            }
        });
    } catch (error) {
        clearTimeout(timeoutId);
        spinBtn.disabled = false;

        if (error.name === 'AbortError') {
            return { error: 'Превышено время ожидания ответа' };
        } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return { error: 'Ошибка соединения с сервером' };
        } else {
            return { error: `Неизвестная ошибка: ${error.message}` };
        }
    }
};