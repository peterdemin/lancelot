''' Specs for core library classes / behaviours ''' 

from lancelot import Spec, verifiable, verify
from lancelot.comparators import ExceptionComparator

@verifiable
def exception_comparator_should_compare_type_and_messsage():
    exception_comparator = ExceptionComparator(IndexError('with message'))
    #TODO: nicer way of forcing spec to use underlying not self
    exception_comparator_equals = exception_comparator.__eq__
    spec = Spec(exception_comparator_equals)
    spec.__call__(IndexError('with message')).should_be(True)
    spec.__call__(IndexError('with different message')).should_be(False)
    spec.__call__(ValueError('with message')).should_be(False)
 
if __name__ == '__main__':
    verify()