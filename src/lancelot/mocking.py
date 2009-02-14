'''
Functionality for specifying object collaborations through "mocks"  

Intended public interface:
 Classes: MockSpec, ExceptionComparator
 Functions: -
 Variables: -

Private interface:
 Classes: MockCall

Copyright 2009 by the author(s). All rights reserved 
'''

from lancelot.verification import UnmetSpecification

class MockCall:
    ''' Wraps an instance of a collaboration for a Mock Specification '''
      
    def __init__(self, mock_spec, name):
        ''' An instance is created by a "mock_spec" for a given method "name" 
        A default instance will_return(None), and expects invocation once() ''' 
        self._mock_spec = mock_spec
        self._name = name
        self._specified_args = ()
        self._specified_kwds = {}
        self._specified_result = (None,)
        self._successive_times = 1
        self._current_time = 0
        
    def __call__(self, *args, **kwds):
        ''' Receive the args specified in a should_collaborate... block 
        while in "specification" mode '''
        self._specified_args = self._mock_spec.comparable_args(args)
        self._specified_kwds = self._mock_spec.comparable_kwds(kwds)
        return self
        
    def will_return(self, *values):
        ''' Specify the return value from the result of the collaboration.
        If a list of values is given they will be iterated over on each
        occasion the collaboration occurs, otherwise the same value will be
        used every time '''
        self._specified_result = values
        return self
    
    def once(self):
        ''' Specify that the collaboration will happen once (the default) '''
        return self.times(1)
    
    def twice(self):
        ''' Specify that the collaboration will happen twice '''
        return self.times(2)
    
    def times(self, num_times):
        ''' Specify that the collaboration will happen num_times '''
        self._successive_times = num_times
        return self
    
    #TODO: ugly?
    def start_collaborating(self):
        ''' Switch from "specification" to "collaboration" mode '''
        self._mock_spec.start_collaborating()
        return self._mock_spec
    
    def description(self):
        ''' Describe this part of the should_collaborate specification '''
        return 'should be collaborating with %s%s' % \
            (self._name, self._format_specified_args())
    
    def _format_specified_args(self):
        ''' Format the args specified in a should_collaborate... block '''
        return self._format_args(self._specified_args, self._specified_kwds)

    def _format_args(self, args, kwds):
        ''' Format args for prettier display '''
        formatted_args = ['%r' % arg for arg in args]
        formatted_args.extend(['%s=%r' % (kwd, value) 
                               for kwd, value in kwds.items()])
        return '(%s)' % ','.join(formatted_args)
    
    def result_of(self, name):
        ''' Check that the collaboration is as specified,
        and return the current value specified by will_return '''
        if name == self._name:
            self._remove_from_spec()
            return self._verify #TODO: _current_result
        raise UnmetSpecification('%s, not %s()' % (self.description(), name))
    
    #TODO: ugly?
    def _remove_from_spec(self):
        ''' Check the number of times that this collaboration was specified
        to occur, and remove this collaboration from those remaining '''         
        self._current_time += 1
        if self._successive_times == self._current_time:
            self._mock_spec.collaboration_verified(self)
    
    def _verify(self, *args, **kwds):
        ''' Check that the collaboration is as specified '''
        if self._specified_args == args and self._specified_kwds == kwds:
            return self._current_result()
        supplied = self._format_args(args, kwds)
        msg = '%s, not %s%s' % (self.description(), self._name, supplied)
        raise UnmetSpecification(msg)

    def _current_result(self):
        ''' The current will_return value for this collaboration '''
        if self._successive_times < self._current_time:
            msg = '%s only %s successive times' % \
                (self.description(), self._successive_times)
            raise UnmetSpecification(msg)
        try:
            result = self._specified_result[self._current_time -1]
        except IndexError:
            result = self._specified_result[0]
        return result

#TODO: use in Raise 
class ExceptionComparator:
    ''' Comparator for handling == comparison with Exception instances. '''
    
    def __init__(self, exception):
        ''' Provides the prototypical instance to compare others against'''
        self._exception = exception
        
    def __eq__(self, other):
        ''' True iff type(other) == type(prototypical exception)
        and str(other) == str(prototypical exception '''
        if type(other) != type(self._exception):
            return False
        if str(other) != str(self._exception):
            return False
        return True

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
