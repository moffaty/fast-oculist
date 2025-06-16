export let map = L.map("map", { attributionControl: false }).setView(
    [51.505, -0.09],
    13
);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {}).addTo(
    map
);

let marker = L.marker([51.5, -0.09]).addTo(map);
marker.bindPopup("Ваше местоположение.").openPopup();

function updateCompass(bearing) {
    const icon = document.getElementById("compass-icon");
    const text = document.getElementById("bearing-text");
    icon.style.transform = `rotate(${bearing - 45}deg)`;
    text.textContent = `${bearing}°`;
}

updateCompass(0);
