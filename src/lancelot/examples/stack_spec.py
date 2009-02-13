import lancelot

class Stack:
    def __init__(self):
        self._items = []
        
    def push(self, value):
        self._items.append(value)
        
    def pop(self):
        return self._items.pop()
        
    def peek(self):
        return self._items[-1]

def new_stack():
    return Stack()

@lancelot.verifiable
def specify_cant_peek_or_pop_from_new_stack():
    lancelot.Spec(Stack, given=new_stack).pop().should_raise(IndexError)
    
    lancelot.Spec(Stack, given=new_stack).peek().should_raise(IndexError)
    
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.pop().should_raise(IndexError)
    spec.then(spec.pop()).should_raise(IndexError)
    
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.peek().should_raise(IndexError)
    spec.then(spec.pop()).should_raise(IndexError)

@lancelot.verifiable
def specify_can_pop_and_peek_pushed_values_from_stack():
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.when(spec.push(value='a'))
    spec.then(spec.peek()).should_be('a')
    spec.then(spec.pop()).should_be('a')
    spec.then(spec.peek()).should_raise(IndexError)
    spec.then(spec.pop()).should_raise(IndexError)
    
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.when(spec.push(value=1))
    spec.then(spec.pop()).should_be(1)
    spec.then(spec.peek()).should_raise(IndexError)
    spec.then(spec.pop()).should_raise(IndexError)
    
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.when(spec.push(value='a'), spec.push(value='b'))
    spec.then(spec.peek()).should_be('b')
    spec.then(spec.pop()).should_be('b')
    spec.then(spec.peek()).should_be('a')
    spec.then(spec.pop()).should_be('a')
    spec.then(spec.pop()).should_raise(IndexError)
    spec.then(spec.peek()).should_raise(IndexError)
    
if __name__ == '__main__':
    lancelot.verify()