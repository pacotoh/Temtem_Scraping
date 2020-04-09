# Pickles save and load

import os
import pickle
import sys
sys.setrecursionlimit(50000)

def save(filename, obj):
    '''Save the object into filename (inside pickles folder).
    If the file exists then save overwrite it.
    '''
    pickle.dump(obj, open(os.path.dirname(__file__) + '/../pickles/' + filename, 'wb'))

def load(filename):
    '''Returns the object inside the pickle inside filename file.'''
    return pickle.load(open(os.path.dirname(__file__) + '/../pickles/' + filename, 'rb'))