__all__ = [
    "ismod",
    "import_all"
]

from os import (
    listdir
)
from os.path import (
    splitext,
    dirname,
    join,
    isdir,
    exists
)
from inspect import (
    stack,
    getmodule
)

def ismod(n):
    if n.endswith(".py"):
        return True
    if n.endswith(".pyd"): # compiled module
        return True
    if not isdir(n):
        return False
    if exists(join(n, "__init__.py")):
        return True
    if exists(join(n, "__init__.pyd")):
        return True
    return False

def import_all():
    frame = stack()[1][0]
    _dir = dirname(getmodule(frame).__file__)
    for n in listdir(_dir):
        if ismod(join(_dir, n)):
            exec("from ." + splitext(n)[0] + " import *", frame.f_globals)
