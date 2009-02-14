''' Specs for core library classes / behaviours ''' 

from lancelot import Spec, verifiable, verify
from lancelot.comparators import Comparator, EqualsEqualsComparator, \
                                 ExceptionComparator, IsSameComparator, \
                                 LessThanComparator, GreaterThanComparator, \
                                 ContainsComparator, OrComparator 

@verifiable
def base_comparator_behaviour():
    ''' base Comparator should always find compared objects unequivalent.
     Base class should also delegate __eq__ to compare_to. '''
    Spec(Comparator(1)).compares_to(1).should_be(False)
    Spec(Comparator(2)).compares_to(2).should_be(False)
    Spec(Comparator(3)).compares_to(int).should_be(False)

    #TODO: nicer way of forcing spec to use underlying __eq__
    base_comparator_equals = Comparator(1).__eq__
    spec = Spec(base_comparator_equals)
    spec.__call__(1).should_be(False)
    spec.__call__(2).should_be(False)
    spec.__call__(int).should_be(False)

@verifiable
def exceptioncomparator_behaviour():
    ''' ExceptionComparator should compare type and messsage '''
    spec = Spec(ExceptionComparator(IndexError('with message')))
    spec.compares_to(IndexError('with message')).should_be(True)
    spec.compares_to(IndexError('different message')).should_be(False)
    spec.compares_to(ValueError('with message')).should_be(False)

@verifiable
def equalscomparator_behaviour():
    ''' EqualsEqualsComparator should compare objects with == '''
    spec = Spec(EqualsEqualsComparator(1))
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(False)
    
    spec = Spec(EqualsEqualsComparator([]))
    spec.compares_to([]).should_be(True)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def issamecomparator_behaviour():
    ''' IsSameComparator should compare objects with "same" / "is" '''
    spec = Spec(IsSameComparator(1))
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(False)
    
    spec = Spec(IsSameComparator([]))
    spec.compares_to([]).should_be(False) 
    
@verifiable
def lessthancomparator_behaviour():
    ''' LessThanComparator should compare objects with < '''
    spec = Spec(LessThanComparator(1))
    spec.compares_to(1).should_be(False)
    spec.compares_to(2).should_be(True)
    spec.compares_to('a').should_be(False)
    
    spec = Spec(LessThanComparator([]))
    spec.compares_to([]).should_be(False)
    spec.compares_to([1]).should_be(True)
    
@verifiable
def greaterthancomparator_behaviour():
    ''' GreaterThanComparator should compare objects with > '''
    spec = Spec(GreaterThanComparator(2))
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(False)
    spec.compares_to('a').should_be(False)
    
    spec = Spec(GreaterThanComparator([1]))
    spec.compares_to([]).should_be(True)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def contains_comparator_behaviour():
    ''' ContainsComparator should compare objects with "in" / "contains" '''
    spec = Spec(ContainsComparator('a'))
    spec.compares_to(['a', 'b']).should_be(True)
    spec.compares_to(['a']).should_be(True)
    spec.compares_to(['b']).should_be(False)
    spec.compares_to('abc').should_be(True)
    spec.compares_to('def').should_be(False)
    spec.compares_to({'a':1}).should_be(True)
    spec.compares_to({'b':'a'}).should_be(False)
    spec.compares_to(2).should_be(False)
    
    spec = Spec(ContainsComparator(1))
    spec.compares_to([1, 2]).should_be(True)
    spec.compares_to([1]).should_be(True)
    spec.compares_to([2]).should_be(False)
    spec.compares_to('12').should_be(False)
    spec.compares_to({1:'a'}).should_be(True)
    spec.compares_to({'b':1}).should_be(False)
    
@verifiable
def or_comparator_behaviour():
    ''' OrComparator should chain "either-or" comparisons together '''
    spec = Spec(OrComparator(1, EqualsEqualsComparator, LessThanComparator))
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(True)
    spec.compares_to('a').should_be(False)

    spec = Spec(OrComparator(1, EqualsEqualsComparator, GreaterThanComparator))
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(False)
    spec.compares_to('a').should_be(False)

if __name__ == '__main__':
    verify()