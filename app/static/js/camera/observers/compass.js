import { Observer } from "../../observer.js"
export class CompassObserver extends Observer {
    constructor(element) {
        super()
      this.element = element;
      console.log(element)
    }
  
  update(angle) {
      this.element.innerHTML = `<strong>Напралвение камеры:</strong> ${angle}°`;
    }
}
