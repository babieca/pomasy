# -*- coding: utf-8 -*-

import random
import datetime
import string

def id_generator(size=6, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def isfloat(x):
    try:
        float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

def readfile(pathf: str):
    fname= pathf
    
    with open(fname) as f:
        content = f.readlines()
    # to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content 
