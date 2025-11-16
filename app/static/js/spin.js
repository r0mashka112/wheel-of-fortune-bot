export const spinWheel = async (player) => {
    const wheel = document.querySelector(".wheel__sectors-container");
    const spinBtn = document.querySelector(".spin-btn");

    try {
        spinBtn.disabled = true;

        const response = await fetch('/api/spin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                telegram_id: player.telegram_id,
                username: player.username
            })
        });

        if (!response.ok) {
            const error = await response.json();
            spinBtn.disabled = false;

            if (error.detail === "You have already spun the wheel") {
                return {'error': 'Вы уже вращали колесо!'};
            } else if (error.detail === 'No prizes available') {
                return {'error': 'Розыгрыш завершился. Все призы закончились'};
            }
        }

        const spinResult = await response.json();

        return new Promise((resolve) => {
            const rotation = Math.ceil(Math.random() * 7200);
            wheel.style.transform = `rotate(${rotation}deg)`;

            wheel.addEventListener('transitionend', () => {
                spinBtn.disabled = false;
                resolve({
                    'success': {
                        telegram_id: player.telegram_id,
                        username: player.username,
                        prize_id: spinResult.prize.id,
                        prize: spinResult.prize.name
                    }
                });
            }, {
                once: true
            });
        });
    } catch (error) {
        spinBtn.disabled = false;
        return {'error': `Ошибка соединения: ${error}`};
    }
};