import unittest

from lalr.grammar import Grammar, Production


class ProductionTestCase(unittest.TestCase):
    def test_name_immutable(self):
        production = Production("A", ("B",))
        with self.assertRaises(AttributeError):
            production.name = "a"

    def test_symbols_immutable(self):
        production = Production("A", ("B",))
        with self.assertRaises(AttributeError):
            production.symbols = ("b",)


class TerminalsTestCase(unittest.TestCase):
    def test_loop(self):
        grammar = Grammar([
            Production("A", ("B",)),
            Production("A", ("x",)),
            Production("B", ("A",)),
        ], )
        self.assertEqual(grammar.terminals, {"x"})

    def test_example(self):
        grammar = Grammar([
            Production("N", ("V", "=", "E")),
            Production("N", ("E",)),
            Production("E", ("V",)),
            Production("V", ("x",)),
            Production("V", ("*", "E")),
        ])
        self.assertEqual(grammar.terminals, {"x", "=", "*"})


class FirstSetsTestCase(unittest.TestCase):
    def test_loop(self):
        grammar = Grammar([
            Production("A", ("B",)),
            Production("A", ("x",)),
            Production("B", ("A",)),
        ])

        self.assertEqual(grammar.first_sets, {
            "x": {"x"},
            "A": {"x"},
            "B": {"x"},
        })

    def test_example(self):
        grammar = Grammar([
            Production("N", ("V", "=", "E")),
            Production("N", ("E",)),
            Production("E", ("V",)),
            Production("V", ("x",)),
            Production("V", ("*", "E")),
        ])

        self.assertEqual(grammar.first_sets, {
            "x": {"x"},
            "=": {"="},
            "*": {"*"},
            "N": {"*", "x"},
            "E": {"*", "x"},
            "V": {"*", "x"},
        })
