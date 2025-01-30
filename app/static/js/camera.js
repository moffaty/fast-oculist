import { CameraController } from "./camera/cameraController.js";

document.addEventListener("DOMContentLoaded", function () {
  const cameraElements = document.querySelectorAll(".video-container");

  cameraElements.forEach(cameraElement => {
    new CameraController(cameraElement);
  });
});