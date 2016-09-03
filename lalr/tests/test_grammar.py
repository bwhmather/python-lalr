import unittest

from lalr.grammar import Grammar, InternalProduction


class TerminalsTestCase(unittest.TestCase):
    def test_loop(self):
        grammar = Grammar([
            InternalProduction("A", ("B",)),
            InternalProduction("A", ("x",)),
            InternalProduction("B", ("A",)),
        ], )
        self.assertEqual(grammar.terminals, {"x"})

    def test_example(self):
        grammar = Grammar([
            InternalProduction("N", ("V", "=", "E")),
            InternalProduction("N", ("E",)),
            InternalProduction("E", ("V",)),
            InternalProduction("V", ("x",)),
            InternalProduction("V", ("*", "E")),
        ])
        self.assertEqual(grammar.terminals, {"x", "=", "*"})


class FirstSetsTestCase(unittest.TestCase):
    def test_loop(self):
        grammar = Grammar([
            InternalProduction("A", ("B",)),
            InternalProduction("A", ("x",)),
            InternalProduction("B", ("A",)),
        ])

        self.assertEqual(grammar.first_sets, {
            "x": {"x"},
            "A": {"x"},
            "B": {"x"},
        })

    def test_example(self):
        grammar = Grammar([
            InternalProduction("N", ("V", "=", "E")),
            InternalProduction("N", ("E",)),
            InternalProduction("E", ("V",)),
            InternalProduction("V", ("x",)),
            InternalProduction("V", ("*", "E")),
        ])

        self.assertEqual(grammar.first_sets, {
            "x": {"x"},
            "=": {"="},
            "*": {"*"},
            "N": {"*", "x"},
            "E": {"*", "x"},
            "V": {"*", "x"},
        })
