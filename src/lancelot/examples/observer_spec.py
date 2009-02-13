import lancelot 

class Observer:
    def notify(self, observable):
        pass
    
class Observable:
    def __init__(self):
        self.observers = []
        
    def add_observer(self, observer):
        self.observers.append(observer)
        
    def send_notification(self):
        for observer in self.observers:
            observer.notify(self)
        
@lancelot.verifiable
def observable_should_notify_observer():
    observer = lancelot.MockSpec()
    observable = Observable()
    spec = lancelot.Spec(observable)
    spec.send_notification().should_collaborate_with()
    
    observer = lancelot.MockSpec()
    observable = Observable()
    spec = lancelot.Spec(observable)
    spec.when(spec.add_observer(observer))
    spec.then(spec.send_notification())
    spec.should_collaborate_with(observer.notify(observable))
    
    observer = lancelot.MockSpec()
    observable = Observable()
    spec = lancelot.Spec(observable)
    spec.when(spec.add_observer(observer), spec.add_observer(observer))
    spec.then(spec.send_notification())
    spec.should_collaborate_with(observer.notify(observable).successive_times(2))
    
if __name__ == '__main__':
    lancelot.verify()