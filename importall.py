__all__ = [
    "ismod",
    "gen_this",
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
    if n.startswith("__init__."):
        return False
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

def iter_import_all_code(frame):
    _dir = dirname(getmodule(frame).__file__)
    for n in listdir(_dir):
        if n == "this.py":
            continue
        if ismod(join(_dir, n)):
            yield "from ." + splitext(n)[0] + " import *"

def gen_import_all_code(frame):
    return "\n".join(iter_import_all_code(frame))

def import_all():
    frame = stack()[1][0]
    exec(gen_import_all_code(frame), frame.f_globals)

def gen_this():
    """ Use this in such a way:
gen_this()
from .this import *

It creates this.py file that does same as `import_all` but the file
can be parsed by IDEs.
    """

    frame = stack()[1][0]
    _dir = _dir = dirname(getmodule(frame).__file__)
    importer_name = join(_dir, "this.py")

    code = gen_import_all_code(frame)

    if exists(importer_name):
        with open(importer_name, "r") as f:
            generate = (f.read() != code)
    else:
        generate = True

    if generate:
        with open(importer_name, "w") as f:
            f.write(code)
