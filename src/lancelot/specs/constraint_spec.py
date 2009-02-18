''' Specs for core library classes / behaviours ''' 

from lancelot import MockSpec, Spec, verifiable, verify
from lancelot.constraints import Constraint, BeEqualTo, CollaborateWith, \
                                 Not, Raise
from lancelot.verification import UnmetSpecification
from lancelot.specs.simple_fns import dont_raise_index_error, number_one, \
                                      raise_index_error, string_abc

@verifiable
def base_constraint_behaviour():
    ''' base Constraint should invoke callable and verify the result.
    Verification should delegate to a comparator, Nothing() by default, 
    that is used to describe the constraint '''
    
    @verifiable
    def should_invoke_callable():
        a_list = []
        with_callable = lambda: a_list.append(True)
        spec = Spec(Constraint())
        spec.verify(with_callable).should_raise(UnmetSpecification)
        spec.then(a_list.__len__).should_be(1)
    
    @verifiable
    def should_use_nothing_comparator():
        spec = Spec(Constraint())
        spec.verify_value(1).should_be(False)
        spec.verify_value(2).should_be(False)
        spec.verify_value(None).should_be(False)
        spec.verify_value(['majestic', 'moose']).should_be(False)
        spec.verify_value({'gumby': 'brain surgeon'}).should_be(False)

    @verifiable
    def verify_should_use_comparator():
        comparator = MockSpec()
        spec = Spec(Constraint(comparator))
        comparator_compares_to = comparator.compares_to(1).will_return(True)
        spec.verify(lambda: 1).should_collaborate_with(comparator_compares_to)
    
    @verifiable
    def desc_should_use_comparator():
        comparator = MockSpec()
        spec = Spec(Constraint(comparator))
        comparator_description = comparator.description()
        comparator_description.will_return('subtitled')
        spec.describe_constraint()
        spec.should_collaborate_with(comparator_description,
                                     and_result='should be subtitled')
        
@verifiable
def raise_behaviour():
    ''' Raise constraint should check that exception is raised
    and that exception type and message are as specified ''' 
    
    @verifiable
    def should_check_type():
        spec = Spec(Raise(IndexError))
        spec.verify(raise_index_error).should_not_raise(UnmetSpecification)
        spec.verify(dont_raise_index_error).should_raise(UnmetSpecification)
    
    @verifiable
    def should_check_message():
        spec = Spec(Raise(IndexError('with message')))
        spec.verify(raise_index_error).should_not_raise(UnmetSpecification)
        
        spec = Spec(Raise(IndexError('with different message')))
        spec.verify(raise_index_error).should_raise(UnmetSpecification)

    @verifiable
    def should_have_meaningful_msg():
        spec = Spec(Raise(IndexError))
        msg = "should raise IndexError"
        spec.describe_constraint().should_be(msg)
        spec.verify(dont_raise_index_error)
        spec.should_raise(UnmetSpecification(msg))

        spec = Spec(Raise(IndexError('with some message')))
        msg = "should raise IndexError('with some message',)"
        spec.describe_constraint().should_be(msg)
        unmet_msg = msg + ", not IndexError('with message',)"
        unmet_specification = UnmetSpecification(unmet_msg)
        spec.verify(raise_index_error).should_raise(unmet_specification)
    
@verifiable
def be_equal_to_behaviour():
    ''' BeEqualTo constraint should raise exception iff objects unequal '''
    spec = Spec(BeEqualTo(1))
    spec.verify(number_one).should_not_raise(UnmetSpecification)

    spec = Spec(BeEqualTo(2))
    msg = 'should be == 2'
    spec.describe_constraint().should_be(msg)
    spec.verify(number_one).should_raise(UnmetSpecification)
    
    spec = Spec(BeEqualTo('abc'))
    spec.verify(string_abc).should_not_raise(UnmetSpecification)

    spec = Spec(BeEqualTo('def'))
    msg = "should be == 'def'"
    spec.describe_constraint().should_be(msg)
    spec.verify(string_abc).should_raise(UnmetSpecification)
    
@verifiable
def not_behaviour():
    ''' Not should raise exception iff underlying check succeeds '''
    spec = Spec(Not(BeEqualTo(2)))
    spec.verify(number_one).should_not_raise(UnmetSpecification)

    spec = Spec(Not(BeEqualTo(1)))
    msg = 'should not be == 1'
    spec.describe_constraint().should_be(msg)
    spec.verify(number_one).should_raise(UnmetSpecification(msg))
    
    spec = Spec(Not(Not(BeEqualTo(2))))
    msg = 'should be == 2'
    spec.describe_constraint().should_be(msg)
    spec.verify(number_one).should_raise(UnmetSpecification(msg))

@verifiable
def collaboratewith_behaviour(): 
    '''CollaborateWith should start collaborations and finally verify them '''
    
    @verifiable
    def should_trap_incorrect_call():
        ''' Specified foo() but bar() called '''
        mock_spec = MockSpec()
        spec = Spec(CollaborateWith(mock_spec.foo()))
        spec.describe_constraint().should_be(mock_spec.foo().description())
        spec.verify(lambda: mock_spec.bar()).should_raise(UnmetSpecification)
    
    @verifiable
    def correct_call_should_be_ok():
        ''' Specified foo() and foo() called '''
        mock_spec = MockSpec()
        spec = Spec(CollaborateWith(mock_spec.foo()))
        spec.verify(lambda: mock_spec.foo())
        spec.should_not_raise(UnmetSpecification)

    @verifiable
    def should_trap_incorrect_args():
        ''' Specified foo(2) then bar(), and foo(1) called '''
        mock_spec = MockSpec()
        collaborations = (mock_spec.foo(2), mock_spec.bar())
        descriptions = [collaboration.description() 
                        for collaboration in collaborations]
        spec = Spec(CollaborateWith(*collaborations))
        spec.describe_constraint().should_be(','.join(descriptions))
        spec.verify(lambda: mock_spec.foo(1)).should_raise(UnmetSpecification)
    
    @verifiable
    def should_trap_incorrect_return():
        ''' Specified and_result="bar" but was "baz" ''' 
        mock_spec = MockSpec()
        spec = Spec(CollaborateWith(mock_spec.foo().will_return('baz'), 
                                    and_result='bar'))
        spec.verify(lambda: mock_spec.foo()).should_raise(UnmetSpecification)

    @verifiable
    def correct_result_should_be_ok():
        ''' Specified and_result="bar" but was "baz"
        Note: and_result refers to the value returned from the callable  
        invoked in verify(), not the return value from the mock. See
        the Hungarian gentleman in the examples for a clearer picture... ''' 
        mock_spec = MockSpec()
        spec = Spec(CollaborateWith(mock_spec.foo().will_return('bar'), 
                                    and_result='bar'))
        spec.verify(lambda: mock_spec.foo())
        spec.should_not_raise(UnmetSpecification)

if __name__ == '__main__':
    verify()
