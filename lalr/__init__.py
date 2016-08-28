from lalr.grammar import Grammar
from lalr.analysis import ParseTable
from lalr.parsing import parse


class Parser(object):
    def __init__(self, productions, target):
        grammar = Grammar(productions)

        self._parse_table = ParseTable(grammar, target)

    def parse(self, tokens, state=None):
        def _action(production, *values):
            return production.action(*values, state=state)

        return parse(self._parse_table, tokens, action=_action)


def compile(productions, target):
    return Parser(productions, target)
