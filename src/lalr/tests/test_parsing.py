import enum
import unittest

import lalr.exceptions
from lalr import Grammar, ParseTable, Production, parse


def nop(production, *args):
    return production.name


class ParseTestCase(unittest.TestCase):
    def test_example(self):
        grammar = Grammar(
            [
                Production("N", ("V", "=", "E")),
                Production("N", ("E",)),
                Production("E", ("V",)),
                Production("V", ("x",)),
                Production("V", ("*", "E")),
            ]
        )
        parse_table = ParseTable(grammar, "N")

        self.assertEqual(
            parse(parse_table, ["x", "=", "*", "x"], action=nop),
            "N",
        )

    def test_bad_example(self):
        grammar = Grammar(
            [
                Production("N", ("V", "=", "E")),
                Production("N", ("E",)),
                Production("E", ("V",)),
                Production("V", ("x",)),
                Production("V", ("*", "E")),
            ]
        )
        parse_table = ParseTable(grammar, "N")

        with self.assertRaises(lalr.exceptions.ParseError) as exc_context:
            parse(parse_table, ["x", "*", "x"], action=nop)

        exc = exc_context.exception
        self.assertEqual(exc.lookahead_token, "*")
        self.assertEqual(exc.expected_symbols, {"="})

    def test_enum_terminals(self):
        class Terminal(enum.Enum):
            VAR = enum.auto()
            EQ = enum.auto()
            STAR = enum.auto()

        grammar = Grammar(
            [
                Production("N", ("V", Terminal.EQ, "E")),
                Production("N", ("E",)),
                Production("E", ("V",)),
                Production("V", (Terminal.VAR,)),
                Production("V", (Terminal.STAR, "E")),
            ]
        )
        parse_table = ParseTable(grammar, "N")

        self.assertEqual(
            parse(
                parse_table,
                [
                    Terminal.VAR,
                    Terminal.EQ,
                    Terminal.STAR,
                    Terminal.VAR,
                ],
                action=nop,
            ),
            "N",
        )

    def test_enum_nonterminals(self):
        class NonTerminal(enum.Enum):
            N = enum.auto()
            E = enum.auto()
            V = enum.auto()

        grammar = Grammar(
            [
                Production(NonTerminal.N, (NonTerminal.V, "=", NonTerminal.E)),
                Production(NonTerminal.N, (NonTerminal.E,)),
                Production(NonTerminal.E, (NonTerminal.V,)),
                Production(NonTerminal.V, ("x",)),
                Production(NonTerminal.V, ("*", NonTerminal.E)),
            ]
        )
        parse_table = ParseTable(grammar, NonTerminal.N)

        self.assertEqual(
            parse(parse_table, ["x", "=", "*", "x"], action=nop),
            NonTerminal.N,
        )
