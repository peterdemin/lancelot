'''
Functionality for expressing the specified behaviour of an object, function
or collaboration.

Intended public interface:
 Classes: Spec, MockSpec 
 Functions: -
 Variables: -
 
Intended for internal use:
 - 

Copyright 2009 by the author(s). All rights reserved 
'''

from lancelot.calling import MockCall, WrapFunction
from lancelot.comparators import ExceptionComparator
from lancelot.constraints import BeAnything, BeEqualTo, \
                                 CollaborateWith, Not, Raise
from lancelot.verification import UnmetSpecification

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

class MockSpec:
    ''' Allows collaborations between objects to be specified e.g.  
    should_collaborate_with (mock_spec.foo(), mock_spec.bar(1), ...) 
    Distinguishes between "specification" mode (aka "record" mode)
    and "collaboration" mode (aka "playback" mode, when the specifications
    are actually verified)
    '''
    
    def __init__(self, comparators=None):
        ''' A new mock specification: created for specifying collaborations 
        comparators are used when verifying that args supplied in a 
        collaboration are those that were specified - by default an
        ExceptionComparator is used to verify Exception args '''
        self._is_collaborating = False
        self._collaborations = []
        if comparators:
            self._comparators = comparators
        else:
            self._comparators = {Exception:ExceptionComparator}
    
    def verify(self):
        ''' Verify that all the specified collaborations have occurred '''
        if len(self._collaborations) > 0:
            raise UnmetSpecification(self._collaborations[0].description())
    
    def __getattr__(self, name):
        ''' Return a mock call for a single collaboration.
        In "specification" mode a new instance is created,
        in "collaboration" mode an existing instance is verified ''' 
        if self._is_collaborating:
            return self._collaboration(name)
        mock = MockCall(self, name)
        self._collaborations.append(mock)
        return mock
        
    def _collaboration(self, name):
        ''' Return an instance of a collaboration (in "collaboration" mode) '''
        if len(self._collaborations) == 0:
            msg = 'should not be collaborating with %s()' % name
            raise UnmetSpecification(msg)
        return self._collaborations[0].result_of(name)
    
    def comparable(self, value):
        ''' Return a comparable value for an arg, 
        using comparators from __init__ ''' 
        for cls, comparator in self._comparators.items():
            if isinstance(value, cls):
                return comparator(value)
        return value
    
    def comparable_args(self, args):
        ''' Convert all args (tuple) into comparable values '''
        return tuple([self.comparable(arg) for arg in args])

    def comparable_kwds(self, kwds):
        ''' Convert all kwd args (dict) into comparable values '''
        comparable_kwds = {}
        for kwd, value in kwds.items():
            comparable_kwds[kwd] = self.comparable(value)
        return comparable_kwds
        
    #TODO: ugly?
    def start_collaborating(self):
        ''' Switch to collaboration mode '''
        self._is_collaborating = True
        
    #TODO: ugly?
    def collaboration_verified(self, mock_call):
        ''' A specified collaboration has finished '''
        self._collaborations.remove(mock_call)
    
