import typing
from types import MappingProxyType

from lalr.utils import Queue


class Production(object):

    __slots__ = ('name', 'symbols')

    name: str
    symbols: typing.Tuple[str, ...]

    def __init__(self, name, symbols):
        if not isinstance(symbols, tuple):
            raise TypeError("expected tuple, but got {cls}".format(
                cls=type(symbols).__name__
            ))
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'symbols', symbols)

    def __setattr__(self, attr, value):
        raise AttributeError("can't set attributes on productions")

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
        return "Production({name}, {symbols})".format(
            name=self.name, symbols=self.symbols,
        )

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.symbols == other.symbols
        )

    def __hash__(self):
        return (
            hash(self.name) ^
            hash(self.symbols)
        )


class Grammar(object):

    def __init__(self, productions):
        self._productions = frozenset(productions)

        symbols = set()
        nonterminals = set()
        # A map from symbols to sets of symbols for which there exist
        # productions where the first symbol is the first element
        has_first_symbol = {}
        for production in self._productions:
            symbols.add(production.name)
            nonterminals.add(production.name)
            symbols.update(production.symbols)
            has_first_symbol.setdefault(
                production.symbols[0], set()
            ).add(production.name)

        self._symbols = frozenset(symbols)
        self._nonterminals = frozenset(nonterminals)
        self._terminals = self._symbols - self._nonterminals

        # A map from symbols to the set of terminals which can appear as the
        # first terminal in a string that the symbol matches
        first_sets = {}

        for terminal in self._terminals:
            # TODO if this is needed it should be folded into the inner loop.
            # kept separate for now so that it's very clear what is happening
            first_sets[terminal] = {terminal}

            if terminal not in has_first_symbol:
                continue

            queue = Queue(has_first_symbol[terminal])

            while queue:
                nonterminal = queue.pop()
                first_sets.setdefault(nonterminal, set()).add(terminal)

                queue.update(has_first_symbol.get(nonterminal, set()))
        self._first_sets = MappingProxyType({
            nonterminal: frozenset(terminals)
            for nonterminal, terminals in first_sets.items()
        })

        # There must be a first set for every symbol in the grammar
        assert (
            frozenset(self._first_sets) ==
            frozenset.union(self._terminals, self._nonterminals)
        )

        # First sets should contain only terminals
        assert not any(
            first_set - self._terminals
            for first_set in self._first_sets.values()
        )

        # There should be a first set for every terminal and non-terminal
        assert self._symbols == frozenset(self._first_sets.keys())

    def terminals(self):
        """
        The set of all symbols that appear on the right hand side of one or
        more productions but have no production of their own.
        """
        return self._terminals

    def nonterminals(self):
        """
        The set of all symbols for which there are production rules.
        """
        return self._nonterminals

    def symbols(self):
        """
        The set of all symbols, both terminal and non-terminal.
        """
        return self._symbols

    def is_terminal(self, symbol):
        return symbol in self._terminals

    def is_nonterminal(self, symbol):
        return symbol in self._nonterminals

    def is_symbol(self, symbol):
        return symbol in self._symbols

    def productions(self, name=None):
        if name is None:
            return self._productions

        return frozenset(
            production for production in self._productions
            if production.name == name
        )

    def first_set(self, symbol):
        """
        Returns the set of terminals that can appear as the first terminal in
        a symbol.  If passed a terminal symbol will just return a one item
        set containing the terminal itself.
        """
        return self._first_sets[symbol]
