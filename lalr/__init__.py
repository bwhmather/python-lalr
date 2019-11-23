import re

from lalr.analysis import ParseTable
from lalr.exceptions import ProductionSpecParseError
from lalr.grammar import Grammar, InternalProduction
from lalr.parsing import parse


_default = object()


_production_spec_symbol_re = re.compile(r'''
    \s*
    (?P<symbol>
        [a-zA-Z0-9-_]+
    )
    (?:
        \ *
        :
        \ *
        (?P<binding>
            [a-zA-Z0-9-_]+
        )
    )?
    \s*
''', re.VERBOSE)  # pylint: disable=no-member


def _parse_production_spec(string):
    cursor = 0

    symbols = []
    bindings = []

    while cursor < len(string):
        mo = _production_spec_symbol_re.match(string, cursor)
        if mo is None:
            raise ProductionSpecParseError('Invalid production spec.')

        assert mo.group('symbol')

        symbols.append(mo.group('symbol'))
        bindings.append(mo.group('binding'))

        cursor = mo.end()

    return tuple(symbols), tuple(bindings)


def _default_action(**kwargs):
    return None


class Production(object):

    __slots__ = ('_name', '_symbols', '_bindings', '_action')

    def __init__(self, name, symbols, bindings=_default, action=None):
        self._name = name

        if isinstance(symbols, str):
            if bindings is not _default:
                raise TypeError(
                    'Production expects either a string spec or tuples of '
                    'symbols and bindings'
                )

            self._symbols, self._bindings = _parse_production_spec(symbols)
        else:
            self._symbols = tuple(symbols)

            if bindings is _default:
                bindings = tuple([None] * len(self._symbols))
            self._bindings = tuple(bindings)

        if action is None:
            action = _default_action
        self._action = action

    @property
    def name(self):
        return self._name

    @property
    def symbols(self):
        """The tuple of symbols that the production matches
        """
        return self._symbols

    @property
    def bindings(self):
        """A tuple of optional argument names that describe how parsed symbols
        should be passed to the action.
        """
        return self._bindings

    def action(self, *values, state=_default):
        kwargs = {
            binding: value
            for binding, value in zip(self.bindings, values)
            if binding is not None
        }

        if state is not _default:
            kwargs.update(state=state)

        return self._action(**kwargs)

    def __len__(self):
        return len(self.symbols)

    def __getitem__(self, index):
        return self.symbols[index]

    def __str__(self):
        return "{name} -> {symbols}".format(
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

    def parse(self, tokens, *, state=_default):
        def _action(production, *values):
            if state is not _default:
                return self._actions[production](*values, state=state)
            else:
                return self._actions[production](*values)

        return parse(
            self._parse_table, tokens, action=_action,
            token_symbol=self.token_symbol, token_value=self.token_symbol,
        )

    @staticmethod
    def token_symbol(token):
        return token

    @staticmethod
    def token_value(token):
        return token


def compile(productions, target):
    return Parser(productions, target)
