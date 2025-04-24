document.addEventListener("DOMContentLoaded", function () {
    const crosshair = document.querySelector(".crosshair");
    const videoIframe = document.querySelector(".video-container iframe");

    crosshair.addEventListener("click", function (e) {
        // Создаем новое событие click
        const clickEvent = new MouseEvent("click", {
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: e.clientX,
            clientY: e.clientY,
            // Добавьте другие необходимые свойства события
        });

        // Отправляем событие в iframe
        if (videoIframe && videoIframe.contentWindow) {
            const iframeDocument =
                videoIframe.contentDocument ||
                videoIframe.contentWindow.document;
            const elementUnderCrosshair = iframeDocument.elementFromPoint(
                e.clientX,
                e.clientY
            );

            if (elementUnderCrosshair) {
                elementUnderCrosshair.dispatchEvent(clickEvent);
            }
        }
    });

    // Делаем crosshair "прозрачным" для событий мыши
    crosshair.style.pointerEvents = "none";
});
