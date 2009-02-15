''' Specs for core library classes / behaviours ''' 

from lancelot import Spec, verifiable, verify
from lancelot.comparators import Comparator, EqualsEquals, \
     ExceptionValue, SameAs, LessThan, GreaterThan, Contain, \
     NoneValue, NotNoneValue, StrEquals, ReprEquals, Anything, Nothing, \
     NotComparator, OrComparator, NotContain, Length, Empty, Type

@verifiable
def base_comparator_behaviour():
    ''' base Comparator should find all compared objects unequivalent.
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
def type_behaviour():
    ''' Type comparator should compare type() '''
    spec = Spec(Type(list))
    spec.compares_to([]).should_be(True)
    spec.compares_to({}).should_be(False)

    spec = Spec(Type([]))
    spec.compares_to([]).should_be(True)
    spec.compares_to({}).should_be(False)
    
@verifiable
def exceptionvalue_behaviour():
    ''' ExceptionValue comparator should compare type and messsage '''
    spec = Spec(ExceptionValue(IndexError('with message')))
    spec.compares_to(IndexError('with message')).should_be(True)
    spec.compares_to(IndexError('different message')).should_be(False)
    spec.compares_to(ValueError('with message')).should_be(False)

    spec = Spec(ExceptionValue(IndexError))
    spec.compares_to(IndexError('with message')).should_be(True)
    spec.compares_to(IndexError('different message')).should_be(True)
    spec.compares_to(ValueError('with message')).should_be(False)

@verifiable
def equalsequals_behaviour():
    ''' EqualsEquals comparator should compare objects with == '''
    spec = Spec(EqualsEquals(1))
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(False)
    
    spec = Spec(EqualsEquals([]))
    spec.compares_to([]).should_be(True)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def sameas_behaviour():
    ''' SameAs comparator should compare objects with "same" / "is" '''
    spec = Spec(SameAs(1))
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(False)
    
    spec = Spec(SameAs([]))
    spec.compares_to([]).should_be(False) 
    
@verifiable
def lessthan_behaviour():
    ''' LessThan comparator should compare objects with < '''
    spec = Spec(LessThan(1))
    spec.compares_to(0).should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to('a').should_be(False)
    
    spec = Spec(LessThan([1]))
    spec.compares_to([]).should_be(True)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def greaterthan_behaviour():
    ''' GreaterThan comparator should compare objects with > '''
    spec = Spec(GreaterThan(1))
    spec.compares_to(2).should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to('a').should_be(False)
    
    spec = Spec(GreaterThan([]))
    spec.compares_to([]).should_be(False)
    spec.compares_to([1]).should_be(True)
    
@verifiable
def contain_behaviour():
    ''' Contain comparator should compare objects with "in" / "contains" '''
    spec = Spec(Contain('a'))
    spec.compares_to(['a', 'b']).should_be(True)
    spec.compares_to(['a']).should_be(True)
    spec.compares_to(['b']).should_be(False)
    spec.compares_to('abc').should_be(True)
    spec.compares_to('def').should_be(False)
    spec.compares_to({'a':1}).should_be(True)
    spec.compares_to({'b':'a'}).should_be(False)
    spec.compares_to(2).should_be(False)
    
    spec = Spec(Contain(1))
    spec.compares_to([1, 2]).should_be(True)
    spec.compares_to([1]).should_be(True)
    spec.compares_to([2]).should_be(False)
    spec.compares_to('12').should_be(False)
    spec.compares_to({1:'a'}).should_be(True)
    spec.compares_to({'b':1}).should_be(False)

@verifiable
def notcontain_behaviour():
    ''' NotContain comparator should negate the behaviour of Contain '''
    spec = Spec(NotContain(1))
    spec.compares_to([1, 2]).should_be(False)
    spec.compares_to([1]).should_be(False)
    spec.compares_to([2]).should_be(True)

@verifiable
def length_behaviour():
    ''' Length comparator should compare len(object) to specified length '''
    spec = Spec(Length(1))
    spec.compares_to([1, 2]).should_be(False)
    spec.compares_to([1]).should_be(True)
    spec.compares_to([2]).should_be(True)
    spec.compares_to('z').should_be(True)
    spec.compares_to('xyz').should_be(False)

@verifiable
def empty_behaviour():
    ''' Empty comparator should compare len(object) to 0 '''
    spec = Spec(Empty())
    spec.compares_to([1, 2]).should_be(False)
    spec.compares_to([1]).should_be(False)
    spec.compares_to([]).should_be(True)
    spec.compares_to('z').should_be(False)
    spec.compares_to('').should_be(True)

@verifiable
def nonevalue_behaviour():
    ''' NoneValue comparator should compare objects with None '''
    spec = Spec(NoneValue())
    spec.compares_to(None).should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to(2).should_be(False)
    spec.compares_to([]).should_be(False)
    spec.compares_to('').should_be(False)

@verifiable
def notnonevalue_behaviour():
    ''' NotNoneValue comparator should compare objects with not-None '''
    spec = Spec(NotNoneValue())
    spec.compares_to(None).should_be(False)
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(True)
    spec.compares_to([]).should_be(True)
    spec.compares_to('').should_be(True)

@verifiable
def strequals_behaviour():
    ''' StrEquals comparator should compare objects with str() '''
    spec = Spec(StrEquals(1))
    spec.compares_to(1).should_be(True)
    spec.compares_to('1').should_be(True)
    spec.compares_to([1]).should_be(False)
    
    spec = Spec(StrEquals('1'))
    spec.compares_to(1).should_be(True)
    spec.compares_to('1').should_be(True)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def reprequals_behaviour():
    ''' ReprEquals comparator should compare objects with repr() '''
    spec = Spec(ReprEquals(1))
    spec.compares_to(1).should_be(True)
    spec.compares_to('1').should_be(False)
    spec.compares_to([1]).should_be(False)
    
    spec = Spec(ReprEquals('1'))
    spec.compares_to('1').should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def notcomparator_behaviour():
    ''' NotComparator should negate other comparisons '''
    spec = Spec(NotComparator(EqualsEquals(1)))
    spec.compares_to(1).should_be(False)
    spec.compares_to('1').should_be(True)
    spec.compares_to([1]).should_be(True)
    
    spec = Spec(NotComparator(EqualsEquals('1')))
    spec.compares_to('1').should_be(False)
    spec.compares_to(1).should_be(True)
    spec.compares_to([1]).should_be(True)
    
@verifiable
def orcomparator_behaviour():
    ''' OrComparator should chain "either-or" comparisons together '''
    spec = Spec(OrComparator(EqualsEquals(2), LessThan(2)))
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(True)
    spec.compares_to(3).should_be(False)
    spec.compares_to('a').should_be(False)

    spec = Spec(OrComparator(EqualsEquals(2), GreaterThan(2)))
    spec.compares_to(2).should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to('a').should_be(False)
    
@verifiable
def anything_behaviour():
    ''' Anything comparator should find all compared objects equivalent. '''
    spec = Spec(Anything())
    spec.compares_to(1).should_be(True)
    spec.compares_to('1').should_be(True)
    spec.compares_to([1]).should_be(True)
    spec.compares_to('xyz').should_be(True)
    
@verifiable
def nothing_behaviour():
    ''' Nothing comparator should never find compared objects equivalent. '''
    spec = Spec(Nothing())
    spec.compares_to(1).should_be(False)
    spec.compares_to('1').should_be(False)
    spec.compares_to([1]).should_be(False)
    spec.compares_to('xyz').should_be(False)

if __name__ == '__main__':
    verify()