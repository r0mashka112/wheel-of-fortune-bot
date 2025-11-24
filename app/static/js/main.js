import { spinWheel } from "/static/js/spin.js";

document.addEventListener('DOMContentLoaded', async () => {
    const spinBtn = document.querySelector(".spin-btn");
    const originalText = spinBtn.textContent;

    const modalOverlay = document.querySelector('.modal-overlay');
    const modalContent = document.querySelector('.modal__content');
    const modalCloseBtn = document.querySelector('.modal__close-btn');

    if (!modalOverlay || !modalContent || !modalCloseBtn) {
        console.error('Элементы модального окна не найдены');
        return;
    }

    const showModal = (message) => {
        modalContent.textContent = message;
        modalOverlay.classList.add('active');
    };

    const hideModal = () => {
        modalOverlay.classList.remove('active');
        try { tg.close(); } catch {}
    };

    modalCloseBtn.addEventListener('click', hideModal);

    const tg = Telegram.WebApp;

    tg.ready();
    tg.expand();

    const player = tg.initDataUnsafe?.user;

    if (!player?.id) {
        showModal('Данные пользователя недоступны');
        return;
    }

    spinBtn.addEventListener('click', async () => {
        spinBtn.disabled = true;
        spinBtn.textContent = 'Вращаем...';

        try {
            const result = await spinWheel({
                telegram_id: player.id,
                username: player.username
            });

            if (result.error) {
                showModal(result.error);
            }
            else if (result.success) {
                showModal(`Вы выиграли: ${result.success.prize}`);

                try {
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
                        const errorText = await response.text();
                        console.error("Ошибка при отправке результата:", errorText);
                    } else {
                        console.log("Результат успешно отправлен на сервер");
                    }
                } catch (sendError) {
                    console.error("Ошибка при отправке результата:", sendError);
                }
            }
        } catch (error) {
            console.error('Критическая ошибка при вращении колеса:', error);
            showModal(`Критическая ошибка при вращении колеса: ${error}`);
        } finally {
            spinBtn.disabled = false;
            spinBtn.textContent = originalText || 'Крутить';
        }
    });
});
