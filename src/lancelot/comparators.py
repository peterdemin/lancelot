'''
Functionality for comparing two object or class / type instances
to determine if they are "equal", with more room for semantic interpretation
than provided by builtins "==" and "is".

Intended public interface:
 Classes: ExceptionComparator
 Functions: -
 Variables: -

Private interface:
 Classes: Comparator

Copyright 2009 by the author(s). All rights reserved 
'''

class Comparator:
    ''' Comparator base class. '''
    pass

#TODO: use in Raise 
class ExceptionComparator(Comparator):
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
