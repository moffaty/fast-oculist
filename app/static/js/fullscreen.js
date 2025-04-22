import { map } from "./index.js";

const cameras = document.querySelectorAll(".video-container");
const mapObject = document.querySelector("#map"); // исправили здесь

function toggleFullscreenBtn(element) {
    const fullscreenBtn = element.querySelector(".fullscreen-btn");
    const isFullscreen = element.classList.toggle("fullscreen");

    if (fullscreenBtn) {
        fullscreenBtn.innerHTML = isFullscreen ? "&#8592;" : "&#9974;";
    }

    const arrows = element.querySelectorAll(".arrow-btn");
    arrows.forEach((arrow) => {
        arrow.style.fontSize = isFullscreen ? "40px" : "";
    });
}

cameras.forEach((camera) => {
    const fullscreenBtn = camera.querySelector(".fullscreen-btn");
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener("click", () =>
            toggleFullscreenBtn(camera)
        );
    }
});

if (mapObject) {
    const fullscreenBtn = mapObject.querySelector(".fullscreen-btn");
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener("click", () => {
            toggleFullscreenBtn(mapObject);
            map.invalidateSize();
        });
    }
}
