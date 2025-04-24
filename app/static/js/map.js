export let map = L.map("map", { attributionControl: false }).setView(
    [51.505, -0.09],
    13
);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {}).addTo(
    map
);

let marker = L.marker([51.5, -0.09]).addTo(map);
marker.bindPopup("Your Location").openPopup();
