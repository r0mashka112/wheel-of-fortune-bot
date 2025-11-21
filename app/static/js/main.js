import { spinWheel } from "/static/js/spin.js";

document.addEventListener('DOMContentLoaded', async () => {
    const spinBtn = document.querySelector(".spin-btn");
    const tg = Telegram.WebApp;

    tg.ready();
    tg.expand();

    const player = tg.initDataUnsafe.user;

    if (player) {
        spinBtn.onclick = async () => {
            try {
                const result = await spinWheel({
                    telegram_id: player.id,
                    username: player.username
                });

                const modalOverlay = document.querySelector('.modal-overlay');
                modalOverlay.classList.toggle('active');

                const modalContent = document.querySelector('.modal__content');

                const modalCloseBtn = document.querySelector('.modal__close-btn');
                modalCloseBtn.onclick = () => {
                    modalOverlay.classList.toggle('active');
                    tg.close();
                };

                if (result.error) {
                    modalContent.innerText = `${result.error}`;
                }
                else if (result.success) {
                    modalContent.innerText = `Вы выиграли: ${result.success.prize}`;

                    const response = await fetch('/api/spin_result', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            telegram_id: player.id,
                            prize: result.success.prize
                        })
                    });

                    if (!response.ok) {
                        console.error("Ошибка при отправке на сервер", await response.text());
                    } else {
                        console.log("Результат успешно отправлен на сервер");
                    }
                }
            } catch (error) {
                console.error('Произошла ошибка при вращении колеса');
            }
        };
    } else {
        console.error('Данные пользователя недоступны');
    }
});
