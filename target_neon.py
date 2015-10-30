import os
import sys

from neon import typeinfo
from neon.parser import Cursor, Parser

__author__ = 'Christopher Nelson'


def run(filename):
    fp = os.open(filename, os.O_RDONLY, 0o777)
    source = ""
    while True:
        data = os.read(fp, 4096)
        if len(data) == 0:
            break

        source += data
    os.close(fp)

    c = Cursor(filename)
    p = Parser()

    found, node = p.type_definition(source, c)
    if not found:
        print("Unable to parse '%s'" % filename)
        return

    scope = typeinfo.new_scope()
    udt = typeinfo.UserDefinedType(node)
    if udt.check(scope):
        print("Program type checks.")
    else:
        print("Program failed type checking.")


def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print("You must supply a filename to execute.")
        return 1

    run(filename)
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
