from lancelot import *
from lancelot.mocking import ExceptionComparator, MockCall
from lancelot.specification import BeType
from lancelot.verification import UnmetSpecification

@verifiable
def making_a_mock_call_should_return_the_mock_call():
    mock_call = MockSpec().foo
    spec = Spec(mock_call)
    spec.__call__().should_be(mock_call)
    
@verifiable
def result_of_a_mock_call_should_verify_the_name_specification():
    mock_call = MockSpec().foo()
    spec = Spec(mock_call)
    spec.result_of('bar').should_raise(UnmetSpecification('should be collaborating with foo(), not bar()'))

    mock_call = MockSpec().foo()
    spec = Spec(mock_call)
    spec.result_of('foo').should_not_raise(UnmetSpecification)

@verifiable
def mock_call_will_return_should_return_mock_call():
    mock_call = MockSpec().foo()
    Spec(mock_call).will_return(1).should_be(mock_call)

@verifiable
def result_of_a_mock_call_should_be_callable_and_return_the_specified_value():
    mock_call = MockSpec().foo()
    mock_call_result = mock_call.result_of('foo')
    spec = Spec(mock_call_result)
    spec.__call__().should_be(None)

    mock_call = MockSpec().foo().will_return(1)
    mock_call_result = mock_call.result_of('foo')
    spec = Spec(mock_call_result)
    spec.__call__().should_be(1)
    
    mock_call = MockSpec().foo().will_return((2,3))
    mock_call_result = mock_call.result_of('foo')
    spec = Spec(mock_call_result)
    spec.__call__().should_be((2,3))

@verifiable
def result_of_a_mock_call_should_verify_the_args_specification():
    mock_call = MockSpec().foo()
    mock_call_result = mock_call.result_of('foo')
    spec = Spec(mock_call_result)
    spec.__call__(1).should_raise(UnmetSpecification('should be collaborating with foo(), not foo(1)'))
    
    mock_call = MockSpec().foo(1)
    mock_call_result = mock_call.result_of('foo')
    spec = Spec(mock_call_result)
    spec.__call__('1').should_raise(UnmetSpecification("should be collaborating with foo(1), not foo('1')"))
    
    mock_call = MockSpec().foo(1)
    mock_call_result = mock_call.result_of('foo')
    spec = Spec(mock_call_result)
    spec.__call__().should_raise(UnmetSpecification('should be collaborating with foo(1), not foo()'))
    
    mock_call = MockSpec().foo(1)
    mock_call_result = mock_call.result_of('foo')
    spec = Spec(mock_call_result)
    spec.__call__(2).should_raise(UnmetSpecification('should be collaborating with foo(1), not foo(2)'))
    
    mock_call = MockSpec().foo(1)
    mock_call_result = mock_call.result_of('foo')
    spec = Spec(mock_call_result)
    spec.__call__(1).should_not_raise(UnmetSpecification)
    
    mock_call = MockSpec().foo(1).will_return(2)
    mock_call_result = mock_call.result_of('foo')
    spec = Spec(mock_call_result)
    spec.__call__(1).should_be(2)
    
    mock_call = MockSpec().bar(keyword='named argument')
    mock_call_result = mock_call.result_of('bar')
    spec = Spec(mock_call_result)
    spec.__call__(keyword='wrong argument').should_raise(UnmetSpecification("should be collaborating with bar(keyword='named argument'), not bar(keyword='wrong argument')"))

    mock_call = MockSpec().bar(keyword='named argument')
    mock_call_result = mock_call.result_of('bar')
    spec = Spec(mock_call_result)
    spec.__call__(bad_keyword='named argument').should_raise(UnmetSpecification("should be collaborating with bar(keyword='named argument'), not bar(bad_keyword='named argument')"))
        
    mock_call = MockSpec().bar(keyword='named argument')
    mock_call_result = mock_call.result_of('bar')
    spec = Spec(mock_call_result)
    spec.__call__(keyword='named argument').should_not_raise(UnmetSpecification)
        
    mock_call = MockSpec().bar(keyword='named argument').will_return('monty')
    mock_call_result = mock_call.result_of('bar')
    spec = Spec(mock_call_result)
    spec.__call__(keyword='named argument').should_be('monty')
        
@verifiable
def mock_call_successive_times_should_return_the_mock_call():
    mock_call = MockSpec().foo()
    Spec(mock_call).successive_times(2).should_be(mock_call)

@verifiable
def result_of_a_mock_call_successive_times_should_iterate_over_specified_value():
    mock_call = MockSpec().foo().successive_times(2).will_return(3,4)
    spec = Spec(mock_call.result_of('foo'))
    spec.__call__().should_be(3)
    spec = Spec(mock_call.result_of('foo'))
    spec.__call__().should_be(4)
    spec = Spec(mock_call.result_of('foo'))
    spec.__call__().should_raise(UnmetSpecification('should be collaborating with foo() only 2 successive times'))
    
    mock_call = MockSpec().bar().successive_times(3).will_return(5)
    spec = Spec(mock_call.result_of('bar'))
    spec.__call__().should_be(5)
    spec = Spec(mock_call.result_of('bar'))
    spec.__call__().should_be(5)
    spec = Spec(mock_call.result_of('bar'))
    spec.__call__().should_be(5)
    spec = Spec(mock_call.result_of('bar'))
    spec.__call__().should_raise(UnmetSpecification('should be collaborating with bar() only 3 successive times'))

@verifiable
def result_of_collaboration_specification_should_be_a_mock_call():
    spec = Spec(MockSpec())
    spec.foo().should(BeType(MockCall))
    spec.bar(12).should(BeType(MockCall))
    spec.baz(keyword='named argument').should(BeType(MockCall))

@verifiable
def after_mock_call_starts_collaborating_then_so_should_its_mock_spec():
    mock_spec = MockSpec()
    mock_call = mock_spec.foo()
    Spec(mock_call).start_collaborating().should_be(mock_spec)
    Spec(mock_spec).bar().should_raise(UnmetSpecification)
    Spec(mock_spec).foo().should_not_raise(UnmetSpecification)

@verifiable
def after_start_collaborating_specified_collaborations_should_be_verified():
    spec = Spec(MockSpec())
    spec.when(spec._start_collaborating())
    spec.then(spec.foo())
    spec.should_raise(UnmetSpecification('should not be collaborating with foo()'))

    spec = Spec(MockSpec())
    spec.when(spec.foo(), spec._start_collaborating())
    spec.then(spec.bar())
    spec.should_raise(UnmetSpecification('should be collaborating with foo(), not bar()'))

    spec = Spec(MockSpec())
    spec.when(spec.foo(), spec.bar(), spec._start_collaborating())
    spec.then(spec.foo()).should_not_raise(UnmetSpecification)
    spec.then(spec.baz()).should_raise(UnmetSpecification('should be collaborating with bar(), not baz()'))
    
    mock = MockSpec()
    mock.foo().successive_times(2).will_return('camelot')
    spec = Spec(mock)
    spec.when(spec._start_collaborating())
    spec.then(spec.foo()).should_not_raise(UnmetSpecification)
    spec.then(spec.foo()).should_not_raise(UnmetSpecification)
    spec.then(spec.foo()).should_raise(UnmetSpecification('should not be collaborating with foo()'))

@verifiable
def after_start_collaborating_unverified_collaborations_should_be_verified():
    spec = Spec(MockSpec())
    spec.when(spec.foo(), spec._start_collaborating())
    spec.then(spec.verify())
    spec.should_raise(UnmetSpecification('should be collaborating with foo()'))
    
    spec = Spec(MockSpec())
    spec.when(spec.foo(), spec._start_collaborating(), spec.foo())
    spec.then(spec.verify())
    spec.should_not_raise(UnmetSpecification)
    
@verifiable
def exception_comparator_should_compare_type_and_messsage():
    exception_comparator = ExceptionComparator(IndexError('with message'))
    #TODO: nicer way of forcing spec to use underlying not self
    exception_comparator_equals = exception_comparator.__eq__
    spec = Spec(exception_comparator_equals)
    spec.__call__(IndexError('with message')).should_be(True)
    spec.__call__(IndexError('with different message')).should_be(False)
    spec.__call__(ValueError('with message')).should_be(False)
    
@verifiable
def exception_comparator_should_be_used_by_comparable_for_exceptions():
    spec = Spec(MockSpec())
    spec._comparable(IndexError('the number of the counting'))
    spec.should(BeType(ExceptionComparator))

    spec._comparable(1).should_be(1)
    
@verifiable
def exception_comparator_should_be_used_when_verifying_arg_specification():
    mock_call = MockSpec().your_mother(TypeError('hamster'))
    mock_call_result = mock_call.result_of('your_mother')
    spec = Spec(mock_call_result)
    spec.__call__(TypeError('hamster')).should_not_raise(UnmetSpecification)
    
    mock_call = MockSpec().your_father(smelt_of=TypeError('elderberries'))
    mock_call_result = mock_call.result_of('your_father')
    spec = Spec(mock_call_result)
    spec.__call__(smelt_of=TypeError('elderberries')).should_not_raise(UnmetSpecification)

class NeverEqualToAnythingComparator:
    def __init__(self, object):
        pass
    def __eq__(self, other):
        return False

@verifiable
def comparators_should_be_over_rideable():
    comparators = {Exception:NeverEqualToAnythingComparator}
    mock_call = MockSpec(comparators=comparators).your_mother(TypeError('hamster'))
    mock_call_result = mock_call.result_of('your_mother')
    spec = Spec(mock_call_result)
    spec.__call__(TypeError('hamster')).should_raise(UnmetSpecification)
    
if __name__ == '__main__':
    verify()