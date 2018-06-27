from types import MappingProxyType

from lalr.utils import Queue


class InternalProduction(object):

    __slots__ = ('_name', '_symbols')

    def __init__(self, name, symbols, action=None):
        self._name = name
        self._symbols = tuple(symbols)

    @property
    def name(self):
        return self._name

    @property
    def symbols(self):
        return self._symbols

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

        # Force first_sets property to evaluate
        self.first_sets

        # There must be a first set for every symbol in the grammar
        assert (
            set(self.first_sets) ==
            set.union(self.terminals, self.nonterminals)
        )

        # First sets should contain only terminals
        assert not any(
            set.difference(first_set, self.terminals)
            for first_set in self.first_sets.values()
        )

        # There should be a first set for every terminal and non-terminal
        assert self.symbols == set(self.first_sets.keys())

    @property
    def terminals(self):
        """
        The set of all symbols that appear on the right hand side of one or
        more productions but have no production of their own.
        """
        return set.difference(self.symbols, self.nonterminals)

    @property
    def nonterminals(self):
        """
        The set of all symbols for which there are production rules.
        """
        return {production.name for production in self.productions()}

    @property
    def symbols(self):
        """
        The set of all symbols, both terminal and non-terminal.
        """
        symbols = set()
        for production in self.productions():
            symbols.add(production.name)
            symbols.update(production.symbols)
        return symbols

    def is_terminal(self, symbol):
        return symbol in self.terminals

    def is_nonterminal(self, symbol):
        return symbol in self.nonterminals

    def productions(self, name=None):
        if name is None:
            return set(self._productions)

        return {
            production for production in self._productions
            if production.name == name
        }

    def _build_first_sets(self):
        # A map from symbols to sets of symbols for which there exist
        # productions where the first symbol is the first element
        has_first_symbol = {}

        for production in self.productions():
            has_first_symbol.setdefault(
                production.symbols[0], set()
            ).add(production.name)

        # A map from symbols to the set of terminals which can appear as the
        # first terminal in a string that the symbol matches
        first_sets = {}

        for terminal in self.terminals:
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

        return first_sets

    @property
    def first_sets(self):
        """
        A map from symbols to sets of terminals that can appear as the first
        terminal in that symbol.  Terminal symbols are included and just map to
        a set containing only themselves
        """
        if not hasattr(self, '_first_sets'):
            self._first_sets = MappingProxyType(self._build_first_sets())

        return self._first_sets
