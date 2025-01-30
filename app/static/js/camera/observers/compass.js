import { Observer } from "../../observer.js"
export class CompassObserver extends Observer {
    constructor(element) {
        super()
        this.element = element;
    }
  
    update(angle) {
      this.element.innerHTML = `<strong>Camera Angle:</strong> ${angle}°`;
    }
}
