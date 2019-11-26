import enum
import unittest

import lalr.exceptions
from lalr import Parser, Production, _parse_production_spec


class ProductionMiniLanguageTestCase(unittest.TestCase):
    def test_symbol(self):
        symbols, bindings = _parse_production_spec('a')

        self.assertEqual(symbols, ('a',))
        self.assertEqual(bindings, (None,))

    def test_symbol_binding(self):
        symbols, bindings = _parse_production_spec('symbol:binding')

        self.assertEqual(symbols, ('symbol',))
        self.assertEqual(bindings, ('binding',))

    def test_multiple_symbol_bindings(self):
        symbols, bindings = _parse_production_spec(
            'symbol_a:binding_a symbol_b:binding_b',
        )

        self.assertEqual(symbols, ('symbol_a', 'symbol_b'))
        self.assertEqual(bindings, ('binding_a', 'binding_b'))

    def test_unbound_symbols(self):
        symbols, bindings = _parse_production_spec(
            'symbol_a symbol_b:binding_b',
        )

        self.assertEqual(symbols, ('symbol_a', 'symbol_b'))
        self.assertEqual(bindings, (None, 'binding_b'))

    def test_whitespace(self):
        symbols, bindings = _parse_production_spec('''
            symbol_a: binding_a
            symbol_b : binding_b
        ''')

        self.assertEqual(symbols, ('symbol_a', 'symbol_b'))
        self.assertEqual(bindings, ('binding_a', 'binding_b'))


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

    def test_enum_terminals(self):
        class Terminal(enum.Enum):
            VAR = enum.auto()
            EQ = enum.auto()
            STAR = enum.auto()

        parser = Parser([
            Production("N", ("V", Terminal.EQ, "E")),
            Production("N", ("E",)),
            Production("E", ("V",)),
            Production("V", (Terminal.VAR,)),
            Production("V", (Terminal.STAR, "E")),
        ], "N")

        parser.parse([Terminal.VAR, Terminal.EQ, Terminal.STAR, Terminal.VAR])

    def test_enum_nonterminals(self):
        class NonTerminal(enum.Enum):
            N = enum.auto()
            E = enum.auto()
            V = enum.auto()

        parser = Parser([
            Production(NonTerminal.N, (NonTerminal.V, "=", NonTerminal.E)),
            Production(NonTerminal.N, (NonTerminal.E,)),
            Production(NonTerminal.E, (NonTerminal.V,)),
            Production(NonTerminal.V, ("x",)),
            Production(NonTerminal.V, ("*", NonTerminal.E)),
        ], NonTerminal.N)

        parser.parse(["x", "=", "*", "x"])
