// Initialize the map
var map = L.map('map').setView([51.505, -0.09], 13);  // Coordinates of the initial map center and zoom level

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
}).addTo(map);

// Optionally, add a marker to the map
var marker = L.marker([51.5, -0.09]).addTo(map);
marker.bindPopup("Your Location").openPopup();