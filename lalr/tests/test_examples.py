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

    def test_single_element_list(self):
        parse(self.parse_table, ["lparen", "string", "rparen"], action=nop)

    def test_missing_closing_paren(self):
        with self.assertRaises(ParseError) as exc_context:
            parse(self.parse_table, ["lparen", "string"], action=nop)

        exc = exc_context.exception
        self.assertEqual(exc.lookahead_token, None)
        self.assertEqual(exc.expected_symbols, {"expression", "rparen"})
