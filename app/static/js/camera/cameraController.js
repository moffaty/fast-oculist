import { CameraSubject } from "./cameraSubject.js";
import { CompassObserver } from "./observers/compass.js";
import { VideoObserver } from "./observers/video.js";
import { CameraVectorEnum } from "./enum.js"

export class CameraController {
  constructor(cameraElement) {
    this.cameraElement = cameraElement;
    this.camera = new CameraSubject();

    const compassElement = this.cameraElement.querySelector(".compass p");
    this.compass = new CompassObserver(compassElement);

    const videoElement = this.cameraElement.querySelector(".video-source");
    this.video = new VideoObserver(videoElement);

    this.camera.subscribe(this.compass);
    this.camera.subscribe(this.video);

    this.initControls();
  }

  initControls() {
    this.cameraElement.querySelector(".arrow-top").addEventListener("click", () => {
        const newAngle = this.camera.angle + 5;
        this.camera.setAngle({ angle: newAngle, source: CameraVectorEnum.TOP });
    });
    
    this.cameraElement.querySelector(".arrow-bottom").addEventListener("click", () => {
        const newAngle = this.camera.angle - 5;
        this.camera.setAngle({ angle: newAngle, source: CameraVectorEnum.BOTTOM });
    });

    this.cameraElement.querySelector(".arrow-left").addEventListener("click", () => {
        const newAngle = this.camera.angle + 5;
        this.camera.setAngle({ angle: newAngle, source: CameraVectorEnum.LEFT });
    });
    
    this.cameraElement.querySelector(".arrow-right").addEventListener("click", () => {
        const newAngle = this.camera.angle - 5;
        this.camera.setAngle({ angle: newAngle, source: CameraVectorEnum.RIGHT });
    });
  }

  initVideo() {}
}
