'''
Functionality for comparing two object or class / type instances
to determine if they are "equivalent", with more room for semantic 
interpretation than provided by builtins "==" and "is".

Intended public interface:
 Classes: ExceptionComparator, EqualsEqualsComparator, IsSameComparator,
     LessThanComparator, GreaterThanComparator, ContainsComparator,
     StrComparator, ReprComparator, NotComparator, OrComparator
 Functions: -
 Variables: -

Private interface:
 Classes: Comparator

Copyright 2009 by the author(s). All rights reserved 
'''

class Comparator:
    ''' Comparator base class. '''
    
    def __init__(self, prototype):
        ''' Provide a prototypical instance to compare others against'''
        self._prototype = prototype
        
    def __eq__(self, other):
        ''' Delegate to compare_to method '''
        return self.compares_to(other)

    def compares_to(self, other):
        ''' Compare prototypical instance and other instance. 
        Always returns False for this base class'''
        return False

class EqualsEqualsComparator(Comparator):
    ''' Comparator for handling comparison using ==. '''
        
    def compares_to(self, other):
        ''' True iff prototypical instance == other '''
        return self._prototype == other

#TODO: use in Raise 
class ExceptionComparator(Comparator):
    ''' Comparator for handling comparison with Exception instances. '''
        
    def compares_to(self, other):
        ''' True iff type(other) == type(prototypical exception)
        and str(other) == str(prototypical exception '''
        if type(self._prototype) != type(other):
            return False
        if str(self._prototype) != str(other):
            return False
        return True

class IsSameComparator(Comparator):
    ''' Comparator for handling comparison using "same". '''
        
    def compares_to(self, other):
        ''' True iff prototypical instance is other '''
        return self._prototype is other

class LessThanComparator(Comparator):
    ''' Comparator for handling comparison using <. '''
        
    def compares_to(self, other):
        ''' True iff prototypical instance < other '''
        try :
            return self._prototype < other
        except TypeError:
            return False

class GreaterThanComparator(Comparator):
    ''' Comparator for handling comparison using >. '''
        
    def compares_to(self, other):
        ''' True iff prototypical instance > other '''
        try :
            return self._prototype > other
        except TypeError:
            return False

class ContainsComparator(Comparator):
    ''' Comparator for handling comparison using "in" / "contains". '''
        
    def compares_to(self, other):
        ''' True iff other contains prototypical instance '''
        try:
            return self._prototype in other
        except (AttributeError, TypeError):
            return False
        
class IsNoneComparator(Comparator):
    ''' Comparator for handling comparison to None. '''
        
    def compares_to(self, other):
        ''' True iff other other is None (ignoring prototypical instance) '''
        return None == other
           
class StrComparator(Comparator):
    ''' Comparator for handling comparison through str(). '''
        
    def compares_to(self, other):
        ''' True iff other str(prototypical instance) == str(other) '''
        return str(self._prototype) == str(other)

class ReprComparator(Comparator):
    ''' Comparator for handling comparison through repr(). '''
        
    def compares_to(self, other):
        ''' True iff other repr(prototypical instance) == repr(other) '''
        return repr(self._prototype) == repr(other)

class NotComparator(Comparator):
    ''' Comparator for handling negative comparisons. '''
    
    def __init__(self, prototype, comparator_to_negate):
        ''' Negate comparator_to_negate for prototype instance '''
        super().__init__(prototype)
        self._comparator_to_negate = comparator_to_negate(prototype)
        
    def compares_to(self, other):
        ''' True iff other comparator_to_negate does not compare_to(other) '''
        return not self._comparator_to_negate.compares_to(other)
        
class OrComparator(Comparator):
    ''' Comparator for chaining comparisons using "either-or". '''
    
    def __init__(self, prototype, either_comparator, or_comparator):
        ''' Chain either_comparator / or_comparator for prototype instance '''
        super().__init__(prototype)
        self._first_comparison = either_comparator(prototype)
        self._second_comparison = or_comparator(prototype)
    
    def compares_to(self, other):
        ''' True iff compare_to(other) is True for either_comparator /
         or_comparator '''
        if self._first_comparison.compares_to(other):
            return True
        return self._second_comparison.compares_to(other)
