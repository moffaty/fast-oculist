import { Subject } from "../subject.js";
export class CameraSubject extends Subject {
    constructor() {
      super()
      this.angle = 45;
    }
  
    setAngle(data) {
      this.angle = data.angle;
      this.notify(data.angle);
    }
}
  