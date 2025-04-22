const cameras = document.querySelectorAll(".video-container");
cameras.forEach(camera => {
    const fullscreenBtn = camera.querySelector(".fullscreen-btn");
    function openFullscreen() {
        fullscreenBtn.innerHTML = "&#8592;"
        fullscreenBtn.style.padding = "5px 10px 5px 10px"; 
        fullscreenBtn.style.top = "94%";
        camera.style.width = "100%";
        camera.style.height = "100%";
        camera.style.position = "fixed";
        camera.style.zIndex = "9999";
        camera.style.opacity = "1";
        camera.style.fontSize = "32px";
        const arrows = document.querySelectorAll(".arrow-btn");
        arrows.forEach(arrow => {
            arrow.style.fontSize = "40px";
        })
    }

    function closeFullscreen() {
        fullscreenBtn.innerHTML = "&#9974;"
        fullscreenBtn.style.padding = "5px 10px 5px 10px"; 
        fullscreenBtn.style.top = "94%";
        camera.style.width = "100%";
        camera.style.height = "100%";
        camera.style.position = "fixed";
        camera.style.zIndex = "9999";
        camera.style.opacity = "1";
        camera.style.fontSize = "32px";
        const arrows = document.querySelectorAll(".arrow-btn");
        arrows.forEach(arrow => {
            arrow.style.fontSize = "40px";
        })
    }
    
    fullscreenBtn.addEventListener("click", openFullscreen);
    
})