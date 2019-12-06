import enum
import unittest

import lalr.exceptions
from lalr import Grammar, InternalProduction, ParseTable, parse


def nop(production, *args):
    return production.name


class ParseTestCase(unittest.TestCase):

    def test_example(self):
        grammar = Grammar([
            InternalProduction("N", ("V", "=", "E")),
            InternalProduction("N", ("E",)),
            InternalProduction("E", ("V",)),
            InternalProduction("V", ("x",)),
            InternalProduction("V", ("*", "E")),
        ])
        parse_table = ParseTable(grammar, "N")

        self.assertEqual(
            parse(parse_table, ["x", "=", "*", "x"], action=nop),
            "N",
        )

    def test_bad_example(self):
        grammar = Grammar([
            InternalProduction("N", ("V", "=", "E")),
            InternalProduction("N", ("E",)),
            InternalProduction("E", ("V",)),
            InternalProduction("V", ("x",)),
            InternalProduction("V", ("*", "E")),
        ])
        parse_table = ParseTable(grammar, "N")

        with self.assertRaises(lalr.exceptions.ParseError):
            parse(parse_table, ["x", "*", "x"], action=nop)

    def test_enum_terminals(self):
        class Terminal(enum.Enum):
            VAR = enum.auto()
            EQ = enum.auto()
            STAR = enum.auto()

        grammar = Grammar([
            InternalProduction("N", ("V", Terminal.EQ, "E")),
            InternalProduction("N", ("E",)),
            InternalProduction("E", ("V",)),
            InternalProduction("V", (Terminal.VAR,)),
            InternalProduction("V", (Terminal.STAR, "E")),
        ])
        parse_table = ParseTable(grammar, "N")

        self.assertEqual(
            parse(parse_table, [
                Terminal.VAR, Terminal.EQ, Terminal.STAR, Terminal.VAR,
            ], action=nop),
            "N",
        )

    def test_enum_nonterminals(self):
        class NonTerminal(enum.Enum):
            N = enum.auto()
            E = enum.auto()
            V = enum.auto()

        grammar = Grammar([
            InternalProduction(
                NonTerminal.N, (NonTerminal.V, "=", NonTerminal.E)
            ),
            InternalProduction(NonTerminal.N, (NonTerminal.E,)),
            InternalProduction(NonTerminal.E, (NonTerminal.V,)),
            InternalProduction(NonTerminal.V, ("x",)),
            InternalProduction(NonTerminal.V, ("*", NonTerminal.E)),
        ])
        parse_table = ParseTable(grammar, NonTerminal.N)

        self.assertEqual(
            parse(parse_table, ["x", "=", "*", "x"], action=nop),
            NonTerminal.N,
        )
