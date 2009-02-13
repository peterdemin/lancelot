from lancelot.verification import UnmetSpecification
import logging

class Spec:
    def __init__(self, spec_for, given=None):
        self._call_stack = []
        self._spec_for = spec_for
        if given:
            self._setup_initial_state(given)
            
    def _setup_initial_state(self, given):
        initial_state = given()
        if type(initial_state) == self._spec_for:
            self._spec_for = initial_state
            return
        msg = 'type(%s) is not %s' % (initial_state, self._spec_for)
        raise TypeError(msg)
            
    def __getattr__(self, name):
        return self._wrap_fn(WrapFunction(self, self._spec_for, name))
        
    def _wrap_fn(self, wrapper):
        self._call_stack.insert(0, wrapper)
        return wrapper
    
    def when(self, *args):
        for i in range(0, len(args)):
            self._call_stack.pop().result()
        return self
    
    def then(self, action):
        if action != self:
            self._wrap_fn(WrapFunction(self, action, ''))
        return self
    
    def should(self, constraint):
        self._constraint = constraint
        constraint.check(self._call_stack.pop().result)
        return self
    
    def should_raise(self, specified):
        return self.should(Raise(specified))

    def should_not_raise(self, unspecified):
        return self.should(Not(Raise(unspecified)))
    
    def should_be(self, specified):
        return self.should(BeEqualTo(specified))
        
    def should_not_be(self, unspecified):
        return self.should(Not(BeEqualTo(unspecified)))
      
    def should_collaborate_with(self, *collaborations):
        return self.should(CollaborateWith(*collaborations))
    
class WrapFunction:
    def __init__(self, within_spec, target, name):
        self._within_spec = within_spec
        self._target = target
        if type(target).__name__ == 'function' and target.__name__ == name:
            self._name = ''
        else:
            self._name = name
        self._args = ()
        self._kwds = {}

    def __call__(self, *args, **kwds):
        self._args = args
        self._kwds = kwds
        return self._within_spec
    
    def result(self):
        logging.debug('wrapper executing %s %s %s %s' % \
                      (self._target, self._name, self._args, self._kwds))
        if self._name:
            return getattr(self._target, self._name)(*self._args, **self._kwds)
        return self._target(*self._args, **self._kwds)
    
class Raise:
    def __init__(self, specified):
        if type(specified) is type(type):
            self._specified_type = specified
            self._specified_msg = None
            msg = ''
        else:
            self._specified_type = type(specified)
            self._specified_msg = str(specified)
            msg = " '%s'" % (specified)
        name = self._specified_type.__name__
        self._description = 'should raise %s%s' % (name, msg)  

    def check(self, result):
        try:
            actual = result()
        except self._specified_type as raised:
            if self._specified_msg:
                self._check_msg(raised)
            return
        raise UnmetSpecification(self.describe_constraint())

    def _check_msg(self, raised):
        msg_constraint = BeEqualTo(self._specified_msg)
        msg_raised = raised.__str__
        try:
            msg_constraint.check(msg_raised)
        except UnmetSpecification as unmet:
            msg = "%s, not '%s'" % (self.describe_constraint(), msg_raised())
            raise UnmetSpecification(msg)

    def describe_constraint(self):
        return self._description
        
class BeEqualTo:
    def __init__(self, specified):
        self._specified = specified
        
    def check(self, result):
        actual = result()
        if actual != self._specified:
            msg = '%s, not %r' % (self.describe_constraint(), actual)
            raise UnmetSpecification(msg)
        
    def describe_constraint(self):
        return 'should be equal to %r' % self._specified
    
class BeType:
    def __init__(self, specified):
        self._specified = specified
        
    def check(self, result):
        actual = result()
        if type(actual) == self._specified:
            return
        msg = '%s, not %s' % (self.describe_constraint(), type(actual))
        raise UnmetSpecification(msg)
        
    def describe_constraint(self):
        return 'should be type %s' % self._specified
        
class Not:
    def __init__(self, constraint):
        self._constraint = constraint
        
    def check(self, result):
        try:
            self._constraint.check(result)
        except UnmetSpecification:
            return
        raise UnmetSpecification(self.describe_constraint())
    
    def describe_constraint(self):
        msg = self._constraint.describe_constraint()
        if msg.startswith('should not '):
            return msg.replace('should not ', 'should ', 1)
        elif msg.startswith('should '):
            return msg.replace('should ', 'should not ', 1)
        return 'Not: ' + msg 
    
class CollaborateWith:
    def __init__(self, *collaborations):
        self._collaborations = collaborations
    
    def check(self, result):
        mock_specs = []
        for collaboration in self._collaborations:
            mock_specs.append(collaboration.start_collaborating())
        result()
        for mock_spec in mock_specs:
            mock_spec.verify()
    
    def describe_constraint(self):
        descriptions = [collaboration.description() 
                        for collaboration in self._collaborations]
        return ','.join(descriptions)
    
#TODO: lessthan, lessthanorequalto, greaterthan, greaterthanorequalto, within