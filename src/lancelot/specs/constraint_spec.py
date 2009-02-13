from lancelot import *
from lancelot.specification import BeEqualTo, BeType, CollaborateWith, Not, Raise
from lancelot.specs import dont_raise_index_error, number_one, raise_index_error, string_abc
from lancelot.verification import UnmetSpecification

@verifiable
def raise_should_check_type_of_exception_is_raised():
    spec = Spec(Raise(IndexError))
    spec.check(dont_raise_index_error).should_raise(UnmetSpecification)
    spec.check(raise_index_error).should_not_raise(UnmetSpecification)
    
@verifiable
def raise_should_check_exception_msg_if_specified():
    spec = Spec(Raise(IndexError('with message')))
    spec.check(raise_index_error).should_not_raise(UnmetSpecification)
    
    spec = Spec(Raise(IndexError('with wrong message')))
    spec.check(raise_index_error).should_raise(UnmetSpecification)
    
@verifiable
def raise_should_describe_difference_between_actual_and_specifed():
    spec = Spec(Raise(IndexError))
    msg = "should raise IndexError"
    spec.describe_constraint().should_be(msg)
    spec.check(dont_raise_index_error).should_raise(UnmetSpecification(msg))

    spec = Spec(Raise(IndexError('with some message')))
    msg = "should raise IndexError 'with some message'"
    spec.describe_constraint().should_be(msg)
    unmet_specification = UnmetSpecification(msg + ", not 'with message'")
    spec.check(raise_index_error).should_raise(unmet_specification)
    
@verifiable
def be_equal_should_raise_exception_iff_objects_unequal():
    spec = Spec(BeEqualTo(1))
    spec.check(number_one).should_not_raise(UnmetSpecification)

    spec = Spec(BeEqualTo(2))
    msg = 'should be equal to 2'
    spec.describe_constraint().should_be(msg)
    spec.check(number_one).should_raise(UnmetSpecification(msg + ', not 1'))
    
    spec = Spec(BeEqualTo('abc'))
    spec.check(string_abc).should_not_raise(UnmetSpecification)

    spec = Spec(BeEqualTo('def'))
    msg = "should be equal to 'def'"
    spec.describe_constraint().should_be(msg)
    spec.check(string_abc).should_raise(UnmetSpecification(msg + ", not 'abc'"))

@verifiable
def be_type_should_raise_exception_iff_types_unequal():
    spec = Spec(BeType(type('silly walk')))
    spec.check(string_abc).should_not_raise(UnmetSpecification)
    
    msg = "should be type <class 'str'>"
    spec.describe_constraint().should_be(msg)
    spec.check(number_one).should_raise(UnmetSpecification(msg + ", not <class 'int'>"))
    
@verifiable
def not_should_raise_exception_iff_underlying_check_succeeds():
    spec = Spec(Not(BeEqualTo(2)))
    spec.check(number_one).should_not_raise(UnmetSpecification)

    spec = Spec(Not(BeEqualTo(1)))
    msg = 'should not be equal to 1'
    spec.describe_constraint().should_be(msg)
    spec.check(number_one).should_raise(UnmetSpecification(msg))
    
    spec = Spec(Not(Not(BeEqualTo(2))))
    msg = 'should be equal to 2'
    spec.describe_constraint().should_be(msg)
    spec.check(number_one).should_raise(UnmetSpecification(msg))

@verifiable
def collaborate_with_should_start_collaborations_and_finally_verify():
    mock_spec = MockSpec()
    spec = Spec(CollaborateWith(mock_spec.foo()))
    spec.describe_constraint().should_be(mock_spec.foo().description())
    spec.check(lambda: mock_spec.bar()).should_raise(UnmetSpecification)
    
    mock_spec = MockSpec()
    spec = Spec(CollaborateWith(mock_spec.foo()))
    spec.check(lambda: mock_spec.foo()).should_not_raise(UnmetSpecification)

    mock_spec = MockSpec()
    collaborations = (mock_spec.foo(1), mock_spec.bar())
    descriptions = [collaboration.description() 
                    for collaboration in collaborations]
    spec = Spec(CollaborateWith(*collaborations))
    spec.describe_constraint().should_be(','.join(descriptions))
    spec.check(lambda: mock_spec.foo(1)).should_raise(UnmetSpecification)

if __name__ == '__main__':
    verify()
