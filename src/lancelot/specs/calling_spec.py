''' Specs for core library classes / behaviours ''' 

from lancelot import Spec, verifiable, verify
from lancelot.calling import WrapFunction
from lancelot.specs.simple_fns import number_one

@verifiable
def wrap_function_behaviour():
    ''' WrapFunction is a callable that wraps another callable.
    It "collects" args when first invoked and passes them to invoke the
    wrapped callable when asked for its result(). '''
    
    @verifiable
    def call_should_return_spec():
        spec = Spec('a') 
        Spec(WrapFunction(spec, None, None)).__call__().should_be(spec)

    @verifiable
    def result_invoke_underlying():
        spec = Spec(WrapFunction(None, 'a', 'startswith'))
        spec.when(spec.__call__('a')).then(spec.result()).should_be(True)
        spec.when(spec.__call__('b')).then(spec.result()).should_be(False)
    
    @verifiable
    def should_wrap_modulefunctions():
        spec = Spec(WrapFunction(None, number_one, 'number_one'))
        spec.when(spec.__call__()).then(spec.result()).should_be(1)

if __name__ == '__main__':
    verify()