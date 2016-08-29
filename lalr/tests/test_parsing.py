import unittest
import lalr.exceptions
from lalr import Parser, Production


class ParseTestCase(unittest.TestCase):
    def test_example(self):
        parser = Parser([
            Production("N", ("V", "=", "E")),
            Production("N", ("E",)),
            Production("E", ("V",)),
            Production("V", ("x",)),
            Production("V", ("*", "E")),
        ], "N")

        parser.parse(["x", "=", "*", "x"])

    def test_bad_example(self):
        parser = Parser([
            Production("N", ("V", "=", "E")),
            Production("N", ("E",)),
            Production("E", ("V",)),
            Production("V", ("x",)),
            Production("V", ("*", "E")),
        ], "N")

        with self.assertRaises(lalr.exceptions.ParseError):
            parser.parse(["x", "*", "x"])
