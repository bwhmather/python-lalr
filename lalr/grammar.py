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
        return "{name} → {symbols}".format(
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
    def _build_first_sets(self):
        """Returns a map from symbols to sets of terminals that can appear as
        the first terminal in that symbol.  Terminal symbols obviously just
        map to a set containing only themselves

        This can be created without needing to look at item sets.
        This requires that the grammar rules are epsilon free.
        """
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

        assert (
            set(first_sets) ==
            set.union(self.terminals, self.nonterminals)
        )

        # First sets should contain only terminals
        assert not any(
            set.difference(first_set, self.terminals)
            for first_set in first_sets.values()
        )

        # There should be a first set for every terminal and non-terminal
        assert self.symbols == set(first_sets)

        self.first_sets = first_sets

    def __init__(self, productions):
        self._productions = frozenset(productions)
        self._build_first_sets()

    @property
    def terminals(self):
        return set.difference(self.symbols, self.nonterminals)

    @property
    def nonterminals(self):
        return {production.name for production in self.productions()}

    @property
    def symbols(self):
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
