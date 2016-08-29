from lalr.grammar import Grammar, Production
from lalr.analysis import ParseTable
from lalr.parsing import parse


class Parser(object):
    def __init__(self, productions, target):

        grammar_productions = []
        self._actions = {}

        for production in productions:
            grammar_production = Production(
                production.name, production.symbols,
            )
            self._actions[grammar_production] = production.action
            grammar_productions.append(grammar_production)

        grammar = Grammar(grammar_productions)

        self._parse_table = ParseTable(grammar, target)

    def parse(self, tokens, state=None):
        def _action(production, *values):
            return self._actions[production](*values, state=state)

        return parse(self._parse_table, tokens, action=_action)


def compile(productions, target):
    return Parser(productions, target)
