from neon.parser import Cursor, Parser

__author__ = 'Christopher Nelson'

from unittest import TestCase


class TestParser(TestCase):
    def test_function_signature(self):
        c = Cursor("test_data")
        p = Parser()
        data = "do_something :: Int String = Float"
        found, node = p.function_signature(data, c)

        self.assertTrue(found)
        self.assertIsNotNone(node)

        self.assertEqual("do_something", node.name)
        self.assertEqual(2, len(node.inputs))
        self.assertEqual(1, len(node.outputs))

    def test_type_definition(self):
        c = Cursor("test_data")
        p = Parser()
        data = "type SomeType Int"
        found, node = p.type_definition(data, c)

        self.assertTrue(found)
        self.assertEqual("SomeType", node.alias_name)
        self.assertEqual("Int", node.type_name)

    def test_adt_type_definition(self):
        c = Cursor("test_data")
        p = Parser()
        data = "type SomeType:\n" \
               "  I Int\n" \
               "  F Float\n" \
               "  S String\n"

        found, node = p.type_definition(data, c)
        self.assertTrue(found)
