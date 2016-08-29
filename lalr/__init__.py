from lalr.grammar import Grammar, InternalProduction
from lalr.analysis import ParseTable
from lalr.parsing import parse
from lalr.constants import START, EMPTY, EOF


def _default_action(*values, state):
    return None


class Production(object):

    __slots__ = ('_name', '_symbols', '_action')

    def __init__(self, name, symbols, action=None):
        self._name = name
        self._symbols = tuple(symbols)

        if action is None:
            action = _default_action
        self._action = action

    @property
    def name(self):
        return self._name

    @property
    def symbols(self):
        return self._symbols

    @property
    def action(self):
        return self._action

    def __len__(self):
        return len(self.symbols)

    def __getitem__(self, index):
        return self.symbols[index]

    def __str__(self):
        return "{name} → {symbols}".format(
            name=self.name,
            symbols=' '.join(str(symbol) for symbol in self.symbols),
        )

    def __repr__(self):
        return "[" + str(self) + "]"

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.symbols == other.symbols and
            self.action == other.action
        )

    def __hash__(self):
        return (
            hash(self.name) ^
            hash(self.symbols) ^
            hash(self.action)
        )


class Parser(object):
    def __init__(self, productions, target):

        grammar_productions = []
        self._actions = {}

        for production in productions:
            grammar_production = InternalProduction(
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


__all__ = ['compile', 'START', 'EMPTY', 'EOF']
