'''
Functionality for expressing the specified behaviour of an object or function.

Intended public interface:
 Classes: Spec, BeAnything, Raise, BeEqualTo, BeType, Not, CollaborateWith 
 Functions: -
 Variables: -
 
Private interface:
 Classes: WrapFunction

Copyright 2009 by the author(s). All rights reserved 
'''

from lancelot.verification import UnmetSpecification
import logging

class Spec:
    ''' Specify the behaviour of an object instance or standalone function '''
    
    def __init__(self, spec_for, given=None):
        ''' A new specification, for an object, class or standalone function.
        Usage: Spec(standalone fn), Spec(object), 
        or Spec(class, given=descriptive_callable_setting_up_initial_state) '''
        self._call_stack = []
        self._spec_for = spec_for
        self._constraint = BeAnything()
        self._given = given
        if given:
            self._setup_initial_state()
            
    def _setup_initial_state(self):
        ''' Set up any given initial state, checking object/class types '''
        initial_state = self._given()
        if isinstance(initial_state, self._spec_for):
            self._spec_for = initial_state
            return
        msg = 'type(%s) is not %s' % (initial_state, self._spec_for)
        raise TypeError(msg)
            
    def __getattr__(self, name):
        ''' Capture the specification of a method invocation '''
        return self._wrap_fn(WrapFunction(self, self._spec_for, name))
        
    def _wrap_fn(self, wrapper):
        ''' Add a method invocation specification to the pending call stack '''
        self._call_stack.insert(0, wrapper)
        return wrapper
    
    def when(self, *args):
        ''' Specify one or more actions occurring before a then() clause '''
        for i in range(0, len(args)):
            self._call_stack.pop().result()
        return self
    
    def then(self, action):
        ''' Specify an action that should()... after a when() clause '''
        if action != self:
            self._wrap_fn(WrapFunction(self, action, ''))
        return self
    
    def should(self, constraint):
        ''' Specify the constraint to be met by action's behaviour '''  
        self._constraint = constraint
        constraint.check(self._call_stack.pop().result)
        return self
    
    def should_raise(self, specified):
        ''' An action's behaviour should raise an exception.
        The specified exception can either be a type, or an instance '''
        return self.should(Raise(specified))

    def should_not_raise(self, unspecified):
        ''' An action's behaviour should not raise an exception. '''
        return self.should(Not(Raise(unspecified)))
    
    def should_be(self, specified):
        ''' An action's behaviour should return a specified value. '''
        return self.should(BeEqualTo(specified))
        
    def should_not_be(self, unspecified):
        ''' An action's behaviour should not return a specified value. '''
        return self.should(Not(BeEqualTo(unspecified)))
      
    def should_collaborate_with(self, *collaborations):
        ''' An action's behaviour should meet the specified collaborations. '''
        return self.should(CollaborateWith(*collaborations))
    
class WrapFunction:
    ''' Wraps a callable that is invoked when the specification is verified '''
    
    def __init__(self, within_spec, target, name):
        ''' Instance used within_spec, wrapping a named target invocation '''
        self._within_spec = within_spec
        self._target = target
        if type(target).__name__ == 'function' and target.__name__ == name:
            self._name = ''
        else:
            self._name = name
        self._args = ()
        self._kwds = {}

    def __call__(self, *args, **kwds):
        ''' Capture the args to be used for the later invocation ''' 
        self._args = args
        self._kwds = kwds
        return self._within_spec
    
    def result(self):
        ''' Perform the actual invocation ''' 
        logging.debug('wrapper executing %s %s %s %s' % \
                      (self._target, self._name, self._args, self._kwds))
        if self._name:
            callable = getattr(self._target, self._name)
            return callable(*self._args, **self._kwds)
        return self._target(*self._args, **self._kwds)
    
class BeAnything:
    ''' Catch-all should... "be anything" constraint specifier '''
    
    def check(self, result):
        ''' Check that the constraint is met '''
        result()
        
    def describe_constraint(self):
        ''' Describe this constraint '''
        return 'should be anything'
    
class Raise:
    ''' Constraint specifying should... "raise exception..." behaviour '''
    
    def __init__(self, specified):
        ''' Specify the exception that should raised.
        May be an exception type or instance '''
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
        ''' Check that the constraint is met '''
        try:
            result()
        except self._specified_type as raised:
            if self._specified_msg:
                self._check_msg(raised)
            return
        raise UnmetSpecification(self.describe_constraint())

    def _check_msg(self, raised):
        ''' Verify the raised exception message '''
        msg_constraint = BeEqualTo(self._specified_msg)
        msg_raised = raised.__str__
        try:
            msg_constraint.check(msg_raised)
        except UnmetSpecification:
            msg = "%s, not '%s'" % (self.describe_constraint(), msg_raised())
            raise UnmetSpecification(msg)

    def describe_constraint(self):
        ''' Describe this constraint '''
        return self._description
        
class BeEqualTo:
    ''' Constraint specifying should... "be == to..." behaviour '''
    
    def __init__(self, specified):
        ''' Specify the value that should be == '''
        self._specified = specified
        
    def check(self, result):
        ''' Check that the constraint is met '''
        actual = result()
        if actual != self._specified:
            msg = '%s, not %r' % (self.describe_constraint(), actual)
            raise UnmetSpecification(msg)
        
    def describe_constraint(self):
        ''' Describe this constraint '''
        return 'should be equal to %r' % self._specified
    
class BeType:
    ''' Constraint specifying should... "be type of..." behaviour '''
    
    def __init__(self, specified):
        ''' Specify what type of thing it should be '''
        self._specified = specified
        
    def check(self, result):
        ''' Check that the constraint is met '''
        actual = result()
        if type(actual) == self._specified:
            return
        msg = '%s, not %s' % (self.describe_constraint(), type(actual))
        raise UnmetSpecification(msg)
        
    def describe_constraint(self):
        ''' Describe this constraint '''
        return 'should be type %s' % self._specified
        
class Not:
    ''' Constraint specifying should... "not..." behaviour '''
    
    def __init__(self, constraint):
        ''' Specify what other constraint it should not be '''
        self._constraint = constraint
        
    def check(self, result):
        ''' Check that the constraint is met '''
        try:
            self._constraint.check(result)
        except UnmetSpecification:
            return
        raise UnmetSpecification(self.describe_constraint())
    
    def describe_constraint(self):
        ''' Describe this constraint '''
        msg = self._constraint.describe_constraint()
        if msg.startswith('should not '):
            return msg.replace('should not ', 'should ', 1)
        elif msg.startswith('should '):
            return msg.replace('should ', 'should not ', 1)
        return 'Not: ' + msg 
    
class CollaborateWith:
    ''' Constraint specifying should... "collaborate with" behaviour '''
    
    def __init__(self, *collaborations):
        ''' Specify what MockSpec collaborations should occur '''
        self._collaborations = collaborations
    
    def check(self, result):
        ''' Check that the constraint is met '''
        mock_specs = []
        for collaboration in self._collaborations:
            mock_specs.append(collaboration.start_collaborating())
        result()
        for mock_spec in mock_specs:
            mock_spec.verify()
    
    def describe_constraint(self):
        ''' Describe this constraint '''
        descriptions = [collaboration.description() 
                        for collaboration in self._collaborations]
        return ','.join(descriptions)
    
#TODO: lessthan, lessthanorequalto, greaterthan, greaterthanorequalto, within

