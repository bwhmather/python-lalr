import unittest

from lalr import Grammar, ParseTable, Production, parse
from lalr.exceptions import ParseError


def nop(production, *args):
    return production.name


class LispTestCase(unittest.TestCase):
    grammar = Grammar([
        Production("list", ("lparen", "rparen")),
        Production("list", ("lparen", "list_body", "rparen")),

        Production("list_body", ("expression",)),
        Production("list_body", ("list_body", "expression")),

        Production("expression", ("list",)),
        Production("expression", ("string",)),
        Production("expression", ("number",)),
        Production("expression", ("symbol",)),
    ])

    parse_table = ParseTable(grammar, "expression")

    def test_two_element_list(self):
        reductions = []
        def _record(production, *args):
            reductions.append(production)

        parse(self.parse_table, ["lparen", "string", "string", "rparen"], action=_record)

        self.assertEqual(reductions, [
            Production("expression", ("string",)),
            Production("list_body", ("expression",)),
            Production("expression", ("string",)),
            Production("list_body", ("list_body", "expression")),
            Production("list", ("lparen", "list_body", "rparen")),
            Production("expression", ("list",)),
        ])

    def test_missing_closing_paren(self):
        with self.assertRaises(ParseError) as exc_context:
            parse(self.parse_table, ["lparen", "string"], action=nop)

        exc = exc_context.exception
        self.assertEqual(exc.lookahead_token, None)
        self.assertEqual(exc.expected_symbols, {"expression", "rparen"})
