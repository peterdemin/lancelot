'''
Functionality for expressing the constraints on behaviour (with should...)

Intended public interface:
 Classes:  BeAnything, Raise, BeEqualTo, BeType, Not, CollaborateWith 
 Functions: -
 Variables: -
 
Intended for internal use:
 Classes: Constraint

Copyright 2009 by the author(s). All rights reserved 
'''

from lancelot.comparators import IsNothingComparator, IsAnythingComparator
from lancelot.verification import UnmetSpecification

class Constraint:
    ''' Base constraint class '''
    
    def __init__(self, comparator=IsNothingComparator()):
        ''' Specify the comparator that is used in verification '''
        self._comparator = comparator
    
    def verify_constraint(self, callable_result):
        ''' Invoke callable_result() and verify() it meets the constraint '''
        value = callable_result()
        return self.verify(value)
        
    def verify(self, value, raised_exception=None):
        ''' Verify that a value meets the constraint '''
        return self._comparator.compares_to(value)
        
    def describe_constraint(self):
        ''' Describe this constraint '''
        return 'should not be anything'    

class BeAnything(Constraint):
    ''' Catch-all should... "be anything" constraint specifier '''
    
    def __init__(self):
        ''' Specify the IsAnything comparator used in verification '''
        super().__init__(IsAnythingComparator())
        
    def describe_constraint(self):
        ''' Describe this constraint '''
        return 'should be anything'
    
class Raise(Constraint):
    ''' Constraint specifying should... "raise exception..." behaviour '''
    
    def __init__(self, specified):
        ''' Specify the exception that should raised.
        May be an exception type or instance '''
        super().__init__()
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
        
class BeEqualTo(Constraint):
    ''' Constraint specifying should... "be == to..." behaviour '''
    
    def __init__(self, specified):
        super().__init__()
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
    
class BeType(Constraint):
    ''' Constraint specifying should... "be type of..." behaviour '''
    
    def __init__(self, specified):
        ''' Specify what type of thing it should be '''
        super().__init__()
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
        
class Not(Constraint):
    ''' Constraint specifying should... "not..." behaviour '''
    
    def __init__(self, constraint):
        ''' Specify what other constraint it should not be '''
        super().__init__()
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
    
class CollaborateWith(Constraint):
    ''' Constraint specifying should... "collaborate with" behaviour '''
    
    def __init__(self, *collaborations):
        ''' Specify what MockSpec collaborations should occur '''
        super().__init__()
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
