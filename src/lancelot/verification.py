import sys, traceback

class UnmetSpecification(Exception):
    pass

class ConsoleListener:    
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        self._stdout = stdout
        self._stderr = stderr
        
    def all_verifiable_starting(self, all_verifiable):
        self._print('Verifying: ', end='', file=self._stdout)
        
    def verification_started(self, fn):
        self._print('.', end='', file=self._stdout)
    
    def specification_met(self, fn):
        pass
    
    def specification_unmet(self, fn, exception):
        msg = 'Specification not met: %s' % exception
        self._print(msg, file = self._stderr)
        #TODO: strip out some of the traceback
        traceback.print_tb(exception.__traceback__, file=self._stderr)

    def all_verifiable_ending(self, all_verifiable, outcome):
        self._print('\n%s' % outcome, file=self._stdout)
        
    def _print(self, msg, end='\n', file=None):
        file = file and file or self._stdout
        print(msg, end=end, file=file)

class AllVerifiable:
    def __init__(self, progress_listener=ConsoleListener()):
        self._fn_list = []
        self._progress_listener = progress_listener
    
    def include(self, verifiable_fn):
        self._fn_list.append(verifiable_fn)
        return self
        
    def total(self):
        return len(self._fn_list)
        
    def verify(self):
        verified = 0
        self._progress_listener.all_verifiable_starting(self)
        for verifiable_fn in self._fn_list:
            verified += self._verify_fn(verifiable_fn)
        outcome = {'total': self.total(), 
                   'verified': verified, 
                   'unverified': self.total() - verified}
        self._progress_listener.all_verifiable_ending(self, outcome)
        return outcome 
    
    def _verify_fn(self, verifiable_fn):
        self._progress_listener.verification_started(verifiable_fn)
        try:
            verifiable_fn()
            self._progress_listener.specification_met(verifiable_fn)
            return 1
        except Exception as e:
            self._progress_listener.specification_unmet(verifiable_fn, e)
            return 0

_all_verifiable = AllVerifiable()

def verifiable(annotated_fn, all_verifiable=_all_verifiable):
    all_verifiable.include(annotated_fn)
    return annotated_fn

def verify(single_verifiable_fn=None):
    if single_verifiable_fn:
        AllVerifiable().include(single_verifiable_fn).verify()
    else:
        _all_verifiable.verify()

# Copyright 2009 by the author(s). All rights reserved #