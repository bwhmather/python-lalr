import unittest

import pytest

from lalr import Grammar, ParseTable, Production, parse
from lalr.exceptions import ParseError


def nop(production, *args):
    return production.name


grammar = Grammar(
    [
        Production("list", ("lparen", "rparen")),
        Production("list", ("lparen", "list_body", "rparen")),
        Production("list_body", ("expression",)),
        Production("list_body", ("list_body", "expression")),
        Production("expression", ("list",)),
        Production("expression", ("string",)),
        Production("expression", ("number",)),
        Production("expression", ("symbol",)),
    ]
)

parse_table = ParseTable(grammar, "expression")


def test_two_element_list():
    reductions = []

    def _record(production, *args):
        reductions.append(production)

    parse(
        parse_table,
        ["lparen", "string", "string", "rparen"],
        action=_record,
    )

    assert reductions == [
        Production("expression", ("string",)),
        Production("list_body", ("expression",)),
        Production("expression", ("string",)),
        Production("list_body", ("list_body", "expression")),
        Production("list", ("lparen", "list_body", "rparen")),
        Production("expression", ("list",)),
    ]


def test_missing_closing_paren():
    with pytest.raises(ParseError) as exc_context:
        parse(parse_table, ["lparen", "string"], action=nop)

    exc = exc_context.value
    assert str(exc) == "expected expression or rparen before EOF"
    assert exc.lookahead_token == None
    assert exc.expected_symbols == {"expression", "rparen"}


def test_extra_closing_paren():
    with pytest.raises(ParseError) as exc_context:
        parse(parse_table, ["lparen", "rparen", "rparen"], action=nop)

    exc = exc_context.value
    assert str(exc) == "expected EOF instead of rparen"
    assert exc.lookahead_token == "rparen"
    assert exc.expected_symbols == set()
