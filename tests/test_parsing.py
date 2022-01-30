import enum

import pytest

import lalr.exceptions
from lalr import Grammar, Left, ParseTable, Production, parse


def nop(production, *args):
    return production.name


def test_example():
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

    assert parse(parse_table, ["x", "=", "*", "x"], action=nop) == "N"


def test_bad_example():
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

    with pytest.raises(lalr.exceptions.ParseError) as exc_context:
        parse(parse_table, ["x", "*", "x"], action=nop)

    exc = exc_context.value
    assert exc.lookahead_token == "*"
    assert exc.expected_symbols == {"="}


def test_enum_terminals():
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

    assert (
        parse(
            parse_table,
            [
                Terminal.VAR,
                Terminal.EQ,
                Terminal.STAR,
                Terminal.VAR,
            ],
            action=nop,
        )
        == "N"
    )


def test_enum_nonterminals():
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

    assert (
        parse(parse_table, ["x", "=", "*", "x"], action=nop) == NonTerminal.N
    )


def test_precedence():
    class Expr:
        pass

    grammar = Grammar(
        [
            Production(Expr, ("x",)),
            Production(Expr, (Expr, "*", Expr)),
            Production(Expr, (Expr, "/", Expr)),
            Production(Expr, (Expr, "+", Expr)),
            Production(Expr, (Expr, "-", Expr)),
        ],
        precedence_sets=[
            Left("+", "-"),
            Left("*", "/"),
        ],
    )
    parse_table = ParseTable(grammar, Expr)

    def _action(production, *args):
        if len(args) == 1:
            return args[0]
        return tuple(args)

    expected = ((("x", "-", "x"), "-", ("x", "*", "x")), "+", "x")
    actual = parse(
        parse_table,
        ["x", "-", "x", "-", "x", "*", "x", "+", "x"],
        action=_action,
    )
    assert actual == expected
