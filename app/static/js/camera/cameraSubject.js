import { Subject } from "../subject.js";
export class CameraSubject extends Subject {
    constructor() {
      super()
      this.angle = 45;
    }
  
    setAngle(newAngle) {
      this.angle = newAngle;
      this.notify();
    }
}
  