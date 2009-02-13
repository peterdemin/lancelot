from lancelot.verification import UnmetSpecification

class MockCall:
    def __init__(self, for_spec, name):
        self._for_spec = for_spec
        self._name = name
        self._specified_result = (None,)
        self._specified_args = ()
        self._specified_kwds = {}
        self._successive_times = 1
        self._current_time = 0
        
    def __call__(self, *args, **kwds):
        self._specified_args = self._for_spec.comparable_args(args)
        self._specified_kwds = self._for_spec.comparable_kwds(kwds)
        return self
        
    def will_return(self, *values):
        self._specified_result = values
        return self
    
    def successive_times(self, num_times):
        self._successive_times = num_times
        return self
    
    def start_collaborating(self):
        self._for_spec._start_collaborating()
        return self._for_spec
    
    def description(self):
        return 'should be collaborating with %s%s' % \
            (self._name, self._format_specified_args())
    
    def _format_specified_args(self):
        return self._format_args(self._specified_args, self._specified_kwds)

    def _format_args(self, args, kwds):
        formatted_args = ['%r' % arg for arg in args]
        formatted_args.extend(['%s=%r' % (kwd, value) 
                               for kwd, value in kwds.items()])
        return '(%s)' % ','.join(formatted_args)
    
    def result_of(self, name):
        if name == self._name:
            self._remove_from_spec()
            return self._verify
        raise UnmetSpecification('%s, not %s()' % (self.description(), name))
    
    def _remove_from_spec(self):
        self._current_time += 1
        if self._successive_times == self._current_time:
            self._for_spec._remove_mock(self)
    
    def _verify(self, *args, **kwds):
        if self._specified_args == args and self._specified_kwds == kwds:
            return self._current_result()
        supplied = self._format_args(args, kwds)
        msg = '%s, not %s%s' % (self.description(), self._name, supplied)
        raise UnmetSpecification(msg)

    def _current_result(self):
        if self._successive_times < self._current_time:
            msg = '%s only %s successive times' % \
                (self.description(), self._successive_times)
            raise UnmetSpecification(msg)
        try:
            result = self._specified_result[self._current_time -1]
        except IndexError:
            result = self._specified_result[0]
        return result

class ExceptionComparator:
    def __init__(self, exception):
        self._exception = exception
        
    def __eq__(self, other):
        if type(other) != type(self._exception):
            return False
        if str(other) != str(self._exception):
            return False
        return True

class MockSpec:
    def __init__(self, comparators=None):
        self._is_collaborating = False
        self._collaborations = []
        if comparators:
            self._comparators = comparators
        else:
            self._comparators = {Exception:ExceptionComparator}
    
    def verify(self):
        if len(self._collaborations) > 0:
            raise UnmetSpecification(self._collaborations[0].description())
    
    def __getattr__(self, name):
        if self._is_collaborating:
            return self._collaboration(name)
        mock = MockCall(self, name)
        self._collaborations.append(mock)
        return mock
        
    def _collaboration(self, name):
        if len(self._collaborations) == 0:
            msg = 'should not be collaborating with %s()' % name
            raise UnmetSpecification(msg)
        return self._collaborations[0].result_of(name)
    
    def _comparable(self, value):
        for cls, comparator in self._comparators.items():
            if isinstance(value, cls):
                return comparator(value)
        return value
    
    def comparable_args(self, args):
        return tuple([self._comparable(arg) for arg in args])

    def comparable_kwds(self, kwds):
        comparable_kwds = {}
        for kwd, value in kwds.items():
            comparable_kwds[kwd] = self._comparable(value)
        return comparable_kwds
        
    def _start_collaborating(self):
        self._is_collaborating = True
        
    def _remove_mock(self, mock):
        self._collaborations.remove(mock)
    
# Copyright 2009 by the author(s). All rights reserved #
