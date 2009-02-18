''' Specs for core library classes / behaviours ''' 

from lancelot import MockSpec, Spec, verifiable, verify
from lancelot.comparators import Type
from lancelot.verification import AllVerifiable, ConsoleListener, \
                                  UnmetSpecification
from lancelot.specs.simple_fns import dont_raise_index_error, number_one, \
                                      raise_index_error, string_abc

class SilentListener(ConsoleListener):
    ''' AllVerifiable Listener that does not print any messages '''
    def __init__(self):
        ''' Override ConsoleListener to redirect write() calls '''
        super().__init__(self, self)
    def write(self, msg):
        ''' Write nothing so that messages are not printed '''
        pass
    
def silent_listener():
    ''' Descriptive fn: creates AllVerifiable instance with SilentListener '''
    return AllVerifiable(listener=SilentListener())

@verifiable
def verifiable_decorator_behaviour(): 
    ''' Decorator should add fn to ALL_VERIFIABLE and return it '''
    all_verifiable = silent_listener()

    spec = Spec(verifiable)
    spec.verifiable(number_one, all_verifiable).should_be(number_one)
    
    num_verifiable_before = all_verifiable.total()
    spec.when(spec.verifiable(number_one, all_verifiable))
    spec.then(all_verifiable.total).should_be(num_verifiable_before + 1)

@verifiable
def all_verif_total_behaviour():
    ''' total() method should increment as verifiable_fn is included '''
    spec = Spec(AllVerifiable, given=silent_listener)
    spec.total().should_be(0)
    
    spec.when(spec.include(raise_index_error))
    spec.then(spec.total()).should_be(1)
    
    spec.when(spec.include(dont_raise_index_error))
    spec.then(spec.total()).should_be(2)

@verifiable
def all_verif_include_behaviour():
    ''' include() method should return self '''
    all_verifiable = silent_listener()
    spec = Spec(all_verifiable)
    spec.include(string_abc).should_be(all_verifiable)

@verifiable
def all_verif_verify_fn_behaviour():
    ''' verify_fn() should execute the fn, handle exceptions gracefully,
    and return 1 for success / 0 for unmet specification'''
    a_list = []
    lambda_list_append = lambda: a_list.append(len(a_list))  
    
    def should_execute_fn():
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.when(spec.verify_fn(verifiable_fn=string_abc))
        spec.then(a_list.__len__).should_be(0)
        
        spec.when(spec.verify_fn(verifiable_fn=lambda_list_append))
        spec.then(a_list.__len__).should_be(1)

    def should_handle_exceptions():
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.verify_fn(raise_index_error).should_not_raise(Exception)
    
    def should_return_0_or_1():
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.verify_fn(verifiable_fn=raise_index_error).should_be(0)
        spec.verify_fn(verifiable_fn=dont_raise_index_error).should_be(1)

    should_execute_fn()
    should_handle_exceptions()
    should_return_0_or_1()
    
@verifiable
def  all_verif_verify_behaviour():
    ''' verify() should verify each included item and 
    return the result of all attempted / successful verifications '''
    def should_verify_each_item():
        a_list = []
        lambda_list_append1 = lambda: a_list.append(0)
        lambda_list_append2 = lambda: a_list.extend((1, 2)) 
        
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.when(spec.include(lambda_list_append1), 
                  spec.include(lambda_list_append2), 
                  spec.verify())
        spec.then(a_list.__len__).should_be(3)

        spec = Spec(AllVerifiable, given=silent_listener)
        spec.verify().should_be({'total':0, 'verified':0, 'unverified':0})

    def should_return_all_results(): 
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.when(spec.include(number_one))
        spec.then(spec.verify())
        spec.should_be({'total':1, 'verified':1, 'unverified':0})
    
        spec.when(spec.include(raise_index_error))
        spec.then(spec.verify())
        spec.should_be({'total':2, 'verified':1, 'unverified':1})
        
    should_verify_each_item()
    should_return_all_results()

@verifiable
def notification_behaviour(): 
    ''' listener should receive notifications AllVerifiable.verify() '''
    
    def unmet_specification():
        ''' Simple fn that raises UnmetSpecification. ''' 
        raise UnmetSpecification()

    listener = MockSpec()
    all_verifiable_with_mock_listener = AllVerifiable(listener)
    results = {'total': 3, 'verified': 1, 'unverified': 2}
    
    spec = Spec(all_verifiable_with_mock_listener)
    spec.when(spec.include(string_abc), 
              spec.include(raise_index_error),
              spec.include(unmet_specification)) 
    spec.then(spec.verify())
    spec.should_collaborate_with(listener.all_verifiable_starting(all_verifiable_with_mock_listener),
                                 listener.verification_started(string_abc),
                                 listener.specification_met(string_abc),
                                 listener.verification_started(raise_index_error),
                                 listener.unexpected_exception(raise_index_error, Type(IndexError)),
                                 listener.verification_started(unmet_specification),
                                 listener.specification_unmet(unmet_specification, Type(UnmetSpecification)),
                                 listener.all_verifiable_ending(all_verifiable_with_mock_listener, results),
                                 and_result = results)

if __name__ == '__main__':
    verify()