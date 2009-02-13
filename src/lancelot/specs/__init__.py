import lancelot 

'''
Sub-package with Specs for the behaviours of classes in the library 
'''

def dont_raise_index_error():
    ''' Simple fn that does nothing. 
    Aids specifying some behaviours around exceptions ''' 
    pass

def raise_index_error():
    ''' Simple fn that raises an index error.
    Aids specifying some behaviours around exceptions ''' 
    raise IndexError('with message')

def number_one():
    ''' Simple fn that returns the number One (1). ''' 
    return 1

def string_abc():
    ''' Simple fn that returns the string "abc". ''' 
    return 'abc'

#TODO: make suite-like functionality easier: not manually adding to list

if __name__ == '__main__':
    ''' Verify all the specs as a collection '''
    import specification_spec, constraint_spec, wrap_spec, \
        verification_spec, mock_spec
    lancelot.verify()
    