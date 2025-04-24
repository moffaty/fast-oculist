import { map } from "./map.js";

const cameras = document.querySelectorAll(".video-container");
console.log(cameras);
const mapObject = document.querySelector("#map"); // исправили здесь

function toggleFullscreen(element) {
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
        fullscreenBtn.addEventListener("click", () => toggleFullscreen(camera));
    }
});

if (mapObject) {
    const fullscreenBtn = mapObject.querySelector(".fullscreen-btn");
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener("click", () => {
            toggleFullscreen(mapObject);
            map.invalidateSize();
        });
    }
}
