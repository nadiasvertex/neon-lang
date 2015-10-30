from unittest import TestCase

from neon import typeinfo
from neon.parser import Cursor, Parser

__author__ = 'Christopher Nelson'


class TestTypeChecker(TestCase):
    def test_adt_type_definition(self):
        c = Cursor("test_data")
        p = Parser()
        data = "type SomeType:\n" \
               "  I Int\n" \
               "  S String\n"

        found, node = p.type_definition(data, c)
        self.assertTrue(found)

        scope = typeinfo.new_scope()
        udt = typeinfo.UserDefinedType(node)
        self.assertTrue(udt.check(scope))
