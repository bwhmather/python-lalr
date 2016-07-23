_START_SYMBOL = '_S'  # TODO
_EOF = '_$'  # TODO


class ConflictError(Exception):
    pass


class ShiftReduceConflictError(ConflictError):
    pass


class ReduceReduceConflictError(ConflictError):
    pass


class Production(object):

    __slots__ = ('_name', '_symbols')

    def __init__(self, name, symbols):
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

    def __init__(self, productions, terminals):
        self._productions = frozenset(productions)
        self._terminals = frozenset(terminals)

    @property
    def terminals(self):
        return set(self._terminals)

    @property
    def nonterminals(self):
        return {production.name for production in self.productions()}

    @property
    def symbols(self):
        return set.union(self.terminals, self.nonterminals)

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


class Queue(object):
    def __init__(self, items=[]):
        self._queued = list(items)
        self._all = set(items)

    def add(self, item):
        if item not in self._all:
            self._queued.append(item)
            self._all.add(item)

    def update(self, items):
        for item in items:
            self.add(item)

    def pop(self):
        return self._queued.pop()

    def __len__(self):
        return len(self._queued)

    def __bool__(self):
        return bool(self._queued)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.pop()
        except IndexError:
            raise StopIteration()


def build_first_sets(grammar):
    """Returns a map from symbols to sets of terminals that can appear as the
    first terminal in that symbol.  Terminal symbols obviously just map to a
    set containing only themselves

    This can be created without needing to look at item sets.
    This requires that the grammar rules are epsilon free.
    """
    # A map from symbols to sets of symbols for which there exist productions
    # where the first symbol is the first element
    has_first_symbol = {}

    for rule in grammar.productions():
        has_first_symbol.setdefault(rule.symbols[0], set()).add(rule.name)

    # A map from symbols to the set of terminals which can appear as the first
    # terminal in a string that the symbol matches
    first_sets = {}

    for terminal in grammar.terminals:
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
        set(first_sets) == set.union(grammar.terminals, grammar.nonterminals)
    )

    # First sets should contain only terminals
    assert not any(
        set.difference(first_set, grammar.terminals)
        for first_set in first_sets.values()
    )

    # There should be a first set for every terminal and non-terminal
    assert grammar.symbols == set(first_sets)

    return first_sets


class Item(object):

    __slots__ = ('_production', '_cursor', '_follow_set')

    def __init__(self, production, cursor, follow_set):
        assert cursor <= len(production)

        # TODO should this be an identifier instead of a concrete object
        self._production = production
        self._cursor = cursor
        self._follow_set = frozenset(follow_set)

    def __hash__(self):
        return (
            hash(self.production) ^
            hash(self._cursor)
        )

    def __eq__(self, other):
        return (
            self.production == other.production and
            self._cursor == other._cursor
        )

    @property
    def cursor(self):
        return self._cursor

    @property
    def name(self):
        return self.production.name

    @property
    def production(self):
        return self._production

    @property
    def symbols(self):
        return self.production.symbols

    @property
    def matched(self):
        return tuple(self.production[:self._cursor])

    @property
    def expected(self):
        return tuple(self.production[self._cursor:])

    @property
    def follow_set(self):
        return set(self._follow_set)

    def __str__(self):
        return "{name} → {matched} • {expected}, {follow_set}".format(
            name=self.name,
            matched=' '.join(str(symbol) for symbol in self.matched),
            expected=' '.join(str(symbol) for symbol in self.expected),
            follow_set='/'.join(str(symbol) for symbol in self.follow_set),
        )

    def __repr__(self):
        return '[' + str(self) + ']'

    def shift(self):
        if self._cursor >= len(self.production):
            raise Exception("out of bounds")

        return Item(
            self.production,
            cursor=self._cursor + 1,
            follow_set=self.follow_set
        )


class ItemSet(object):
    def __init__(self, kernel, derived):
        self._kernel = frozenset(kernel)
        self._derived = frozenset(derived)

    @property
    def kernel(self):
        return set(self._kernel)

    @property
    def derived(self):
        return set(self._derived)

    @property
    def items(self):
        return set.union(
            self.kernel,
            self.derived,
        )

    def terminals(self):
        terminals = set()
        for item in self.items:
            terminals.update(item.terminals())
        return terminals

    def nonterminals(self):
        terminals = set()
        for item in self.items:
            terminals.update(item.terminals())
        return terminals

    def __eq__(self, other):
        return self.kernel == other.kernel


def _build_derived_items(grammar, kernel):
    """Given a core set of items and a grammar, recursively expand
    non-terminals into new items until there are no non-terminals left.

    :param grammar:
        A grammar, obviously.

    :param kernel:
        A :class:`set` of :class:`Item`s that make up the kernel of an item set
    """
    # We assume that (with the exception of the starting symbol which we can't
    # reach from any other rule), the cursor will never appear at the beginning
    # of an item in a kernel.  This means that items in the kernel will not
    # also be in the derived set.

    # A map from symbols to sets of terminals that can follow them.  This is
    # used at the end when transforming productions to items
    follow_sets = {}

    # Queue of symbols that should be processed into items
    symbol_queue = Queue()

    grammar.first_sets = build_first_sets(grammar)  # TODO TODO TODO

    for item in kernel:
        if not item.expected:
            continue

        symbol, *rest = item.expected

        if grammar.is_terminal(symbol):
            continue

        # Add new non-terminals to the follow set
        follow_set = follow_sets.setdefault(symbol, set())

        if rest:
            follow_set.update(grammar.first_sets[rest[0]])
        else:
            follow_set.update(item.follow_set)

        # Queue for processing
        symbol_queue.add(symbol)

    productions = set()

    immediate_dependants = {}

    # Expand set of derived productions
    for symbol in symbol_queue:
        for production in grammar.productions(symbol):
            productions.add(production)

            # Find the next symbol and the tuple of symbols following it.
            # As the grammar should have been converted to epsilon free form,
            # and the cursor will always be at the beginning, we can be sure
            # that there will be at least one item and the check can be skipped
            first, *rest = production.symbols

            if grammar.is_terminal(first):
                continue

            symbol_queue.add(first)

            # First we update the follow sets for each symbol.
            # As cycles are possible we need to make sure that we update the
            # follow sets of non-terminals that we have already expanded
            if rest:
                new_items = grammar.first_sets[rest[0]]
            else:
                new_items = follow_sets.get(production.name, set())

                # Make sure that the first symbol gets updated when new items
                # are added to the follow set of the current symbol
                immediate_dependants.setdefault(
                    production.name, set()
                ).update(first)

            follow_sets.setdefault(first, set()).update(new_items)

            # The set of non-terminals that can be reduced to the current
            # symbol, either directly or via some number of intermediate steps
            dependants = set()

            # We build up the set of dependants by iterating over the symbols
            # that are a dependant of the first symbol, and recursively over
            # their dependants, processing each symbol only once.
            # The dependants queue keeps track of what has been done, and what
            # needs to be done.
            dependants_queue = Queue({first})

            # Build the set
            for dependant in dependants_queue:
                if dependant not in immediate_dependants:
                    continue

                dependants_queue.update(immediate_dependants[dependant])
                dependants.update(immediate_dependants[dependant])

            # Update the follow sets of all dependant symbols
            for dependant in dependants:
                follow_sets[dependant].update(new_items)

    # Turn productions and follow sets into items
    return {
        Item(production, cursor=0, follow_set=follow_sets[production.name])
        for production in productions
    }


def merge_items(a, b):
    if a.production != b.production or a.cursor != b.cursor:
        raise Exception('Item cores do not match')

    return Item(a.production, a._cursor, set.union(a.follow_set, b.follow_set))


def merge_kernels(kernel_a, kernel_b):
    items_by_core_a = {
        (item.matched, item.expected): item for item in kernel_a.kernel
    }
    items_by_core_b = {
        (item.matched, item.expected): item for item in kernel_b.kernel
    }

    assert set(items_by_core_a) == set(items_by_core_b)

    return {
        merge_items(items_by_core_a[core], items_by_core_b[core])
        for core in items_by_core_a
    }


def build_item_set(grammar, kernel):
    return ItemSet(kernel, _build_derived_items(grammar, kernel))


def item_set_transitions(grammar, item_set):
    kernels = {}

    for item in item_set.items:
        if not item.expected:
            continue

        symbol, *rest = item.expected

        kernel = kernels.setdefault(symbol, set())
        kernel.add(Item(item.production, item.cursor + 1, item.follow_set))

    return {
        symbol: frozenset(kernel)
        for symbol, kernel in kernels.items()
    }


def _kernel_core(kernel):
    return frozenset((item.matched, item.expected) for item in kernel)


def build_transition_table(grammar, target):
    '''Build the item sets, and map out the corresponding transitions for a
    grammar that accepts the given target.
    '''
    starting_item = Item(
        Production(_START_SYMBOL, {target, }), cursor=0, follow_set={_EOF},
    )

    # A list of item sets.  Item sets are identified by index.  We initialise
    # it with a new item set with the start symbol as its kernel
    item_sets = []

    # A list, with items corresponding to the sets `item_sets`  of
    # dictionaries mapping from symbols to item set indexes
    transitions = []

    kernel_queue = Queue([
        frozenset({starting_item})
    ])

    # A map from kernel cores, frozen sets of tuples of matched and expected
    # strings without a follow set, to item set indexes.  This is used to do
    # LALR state merging
    # TODO does the starting item need to be put in this map?
    item_sets_by_core = {}

    for kernel in kernel_queue:
        if _kernel_core(kernel) in item_sets_by_core:
            item_set_index = item_sets_by_core[_kernel_core(kernel)]
            kernel = merge_kernels(item_sets[item_set_index].kernel, kernel)
            item_set = build_item_set(grammar, kernel)
            item_sets[item_set_index] = item_set
            transitions[item_set_index] = item_set_transitions(
                grammar, item_set
            )
        else:
            item_set_index = len(item_sets)
            item_set = build_item_set(grammar, kernel)
            item_sets_by_core[_kernel_core(kernel)] = item_set_index
            item_sets.append(item_set)
            transitions.append(item_set_transitions(grammar, item_set))

        kernel_queue.update(transitions[item_set_index].values())

    transitions = [
        {
            symbol: item_sets_by_core[_kernel_core(kernel)]
            for symbol, kernel in transition_map.items()
        }
        for transition_map in transitions
    ]
    return item_sets, transitions


def build_shift_table(grammar, item_sets, item_set_transitions):
    '''Returns a list of maps from terminal symbols to shift actions.

    A shift action is simply an index into the item_set array.
    '''
    shifts = []
    for transitions in item_set_transitions:
        shifts.append({
            symbol: state
            for symbol, state in item_set_transitions
            if grammar.is_terminal(symbol)
        })
    return shifts


def build_goto_table(grammar, item_sets, item_set_transitions):
    '''Returns a list of dictionaries mapping from non-terminal symbols to the
    state that should follow.

    The items in the list correspond to items in the list of item sets.
    '''
    gotos = []
    for transitions in item_set_transitions:
        gotos.append({
            symbol: state
            for symbol, state in item_set_transitions
            if grammar.is_nonterminal(symbol)
        })
    return gotos


def build_reduction_table(grammar, item_sets, item_set_transitions):
    '''Returns a list of dictionaries mapping from terminal symbols to reduce
    actions.

    Reduce actions are represented simply by a reference to a rule.
    The items in the list of reduction dictionaries correspond to items in the
    list of item sets.
    '''
    reductions = []
    for item_set in item_sets:
        item_set_reductions = {}
        for item in item_set:
            if item.expected:
                continue

            for terminal in item.follow_set:
                if terminal in item_set_reductions:
                    raise ReduceReduceConflictError()
                item_set_reductions[terminal] = item.production
        reductions.append(item_set_reductions)
    return reductions


def check_shift_reduce_conflicts():
    '''Check for conflicts between a shift table and a reduce table
    '''
    pass
