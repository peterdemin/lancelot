import lancelot 

def dont_raise_index_error():
    pass

def raise_index_error():
    raise IndexError('with message')

def number_one():
    return 1

def string_abc():
    return 'abc'

if __name__ == '__main__':
    #TODO: make suite-like functionality easier: not manually adding to list
    import specification_spec, constraint_spec, wrap_spec, \
        verification_spec, mock_spec
    lancelot.verify()