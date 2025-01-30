export class Subject {
    constructor() {
      this.observers = [];
    }
  
    subscribe(observer) {
      this.observers.push(observer);
    }
  
    unsubscribe(observer) {
      this.observers = this.observers.filter(sub => sub !== observer);
    }
  
    notify() {
      this.observers.forEach(observer => observer.update(this.angle));
    }
  }
  