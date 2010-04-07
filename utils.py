# author: Hasan Veldstra <hasan.veldstra@gmail.com>
# license: MIT

import os
import fnmatch

try:
    import simplejson as json
except:
    import json

def locate(pattern, root=os.getcwd()):
    """
    Generate of all files in a directory that match the pattern.
    """
    for path, dirs, files in os.walk(root):
        for filename in [os.path.abspath(os.path.join(path, filename)) for filename in files if fnmatch.fnmatch(filename, pattern)]:
            yield filename

def sort_by_value(d):
    """
    Sort dict by numeric value.
    """
    return sorted(d.iteritems(), key=lambda (k, v): (v, k), reverse=True)

def flatten(x):
    """
    Return flat list of items from all sub-sequences in list x.
    """
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def slurp(fn):
    """
    Read text file into a string.
    """
    f = open(fn)
    s = f.read()
    f.close()
    return s
    
def write(fn, data):
    """
    Write string to a file.
    """
    f = open(fn, "w")
    f.write(data)
    f.close()
    return True
    
def load_json(filename):
    """
    Return datastructure from JSON data in a file.
    """
    return json.loads(slurp(filename))
    
def dump_as_json(filename, datastructure):
    """
    Writes datastructure as JSON into a file.
    """    
    write(filename, json.dumps(datastructure, sort_keys=True, indent=4))