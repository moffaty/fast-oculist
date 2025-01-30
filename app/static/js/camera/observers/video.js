import { Observer } from "../../observer.js"
export class VideoObserver extends Observer {
    constructor(element) {
        super()
        this.element = element;
    }
  
    update(src) {
      this.element.src = src;
    }
}
