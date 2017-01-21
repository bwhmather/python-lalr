import re


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
            raise Exception('Invalid production spec.')

        assert mo.group('symbol')

        symbols.append(mo.group('symbol'))
        bindings.append(mo.group('binding'))

        cursor = mo.end()

    return tuple(symbols), tuple(bindings)


def _default_action(**kwargs):
    return None


class Production(object):

    __slots__ = ('_name', '_symbols', '_bindings', '_action')

    def __init__(self, name, symbols, bindings, action=None):
        self._name = name

        #: The tuple of symbols that the production matches
        self._symbols = tuple(symbols)

        #: A tuple of optional argument names that describe how parsed symbols
        #: should be passed to the action.
        self._bindings = tuple(bindings)

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
    def bindings(self):
        return self._bindings

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
