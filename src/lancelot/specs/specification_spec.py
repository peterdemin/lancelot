from lancelot import *
from lancelot.specification import BeType, Not, WrapFunction
from lancelot.specs import dont_raise_index_error, number_one, raise_index_error, string_abc
from lancelot.verification import UnmetSpecification

@verifiable
def unmet_should_raise_constraint_raises_exception():
    ''' should_raise() and should_not_raise() are the only 
    "atomic" parts that require assertions. All other 
    parts can be bootstrap-tested from these functions. 
    '''
    spec1 = Spec(dont_raise_index_error)
    try:
        spec1.dont_raise_index_error().should_raise(IndexError)
        assert False
    except UnmetSpecification:
        pass
    
    spec2 = Spec(raise_index_error)
    try:
        spec2.raise_index_error().should_not_raise(IndexError)
        assert False
    except UnmetSpecification:
        pass
    
@verifiable
def number_one_should_be_one():
    ''' Basic specification of the Spec.should...() methods'''
    spec = Spec(number_one)
    spec.number_one().should_be(1)
    spec.number_one().should_not_be(2)
    spec.number_one().should_not_be('a')

@verifiable
def string_abc_should_be_abc():
    ''' More basic specification for the Spec.should...() methods'''
    spec = Spec(string_abc)
    spec.string_abc().should_be('abc')
    spec.string_abc().should_not_be('a')
    spec.string_abc().should_not_be(2)
    
@verifiable
def after_adding_item_to_empty_list_then_its_length_should_be_one():
    ''' Basic spec for the after()...then() sequence'''
    spec = Spec([])
    spec.when(spec.append(object())).then(spec.__len__()).should_be(1)

def empty_list():
    return []

@verifiable
def given_empty_list_after_adding_item_then_its_length_should_be_one():
    ''' Basic spec for given=...after()...then() sequence'''
    spec = Spec(type([]), given=empty_list)
    spec.when(spec.append('monty')).then(spec.__len__()).should_be(1)

def spec_for_dict_given_empty_list():
    return Spec(type({}), given=empty_list)

@verifiable
def spec_for_dict_given_empty_list_should_throw_tpye_error():
    ''' Spec for check that given=... is correct type '''
    spec = Spec(spec_for_dict_given_empty_list)
    type_error = TypeError("type([]) is not <class 'dict'>")
    spec.spec_for_dict_given_empty_list().should_raise(type_error)

def getattr_should_from_spec():
    return getattr(Spec('grail'), 'should')

def getattr_len_from_spec():
    return getattr(Spec('grail'), 'len')

@verifiable
def getattr_from_spec_should_return_wrapper_for_unknown_attributes():
    ''' Spec for internal use of __getattr__() '''
    spec = Spec(getattr_should_from_spec)
    spec.getattr_should_from_spec().should(Not(BeType(WrapFunction)))
    
    spec = Spec(getattr_len_from_spec)
    spec.getattr_len_from_spec().should(BeType(WrapFunction))

@verifiable
def then_method_should_wrap_callable_fns_outside_the_spec_itself():
    ''' Spec for then()... actions that call fns outside the spec itself '''
    spec = Spec([])
    spec.when(spec.append('brian'))
    spec.then([].__len__).should_be(0)
    
if __name__ == '__main__':
    verify()