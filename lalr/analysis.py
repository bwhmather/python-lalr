from types import MappingProxyType

from lalr.constants import EOF, START
from lalr.exceptions import (
    ReduceReduceConflictError, ShiftReduceConflictError,
)
from lalr.grammar import InternalProduction
from lalr.utils import Queue


class _Item(object):
    """
    Class representing the progress of a parser through a production.

    These are grouped into item sets, where each item represents one possible
    location within a production given what has come before.
    """

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
            hash(self._cursor) ^
            hash(self._follow_set)
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.production == other.production and
            self._cursor == other._cursor and
            self._follow_set == other.follow_set
        )

    @property
    def cursor(self):
        """
        A count of how many symbols in the production have been passed.
        """
        return self._cursor

    @property
    def production(self):
        return self._production

    @property
    def name(self):
        """
        The symbol that the items production is an expansion of.
        """
        return self.production.name

    @property
    def symbols(self):
        """
        A tuple of the symbols in the production this item points to.
        """
        return self.production.symbols

    @property
    def matched(self):
        """
        A tuple of the symbols in the item's production that have already been
        found by the parser.
        """
        return tuple(self.production[:self._cursor])

    @property
    def expected(self):
        """
        A tuple of the symbols in the item's production that will need to be
        found for the whole production to be matched.
        """
        return tuple(self.production[self._cursor:])

    @property
    def follow_set(self):
        """
        The set of terminal symbols that can come next if the string matches
        this production.
        """
        return set(self._follow_set)

    def __str__(self):
        return "{name} -> {matched} * {expected}, {follow_set}".format(
            name=self.name,
            matched=' '.join(str(symbol) for symbol in self.matched),
            expected=' '.join(str(symbol) for symbol in self.expected),
            follow_set='/'.join(str(symbol) for symbol in self.follow_set),
        )

    def __repr__(self):
        return '[' + str(self) + ']'


class _ItemSet(object):
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

    def __eq__(self, other):
        return self.kernel == other.kernel

    def __iter__(self):
        return iter(self.items)


def _build_derived_items(grammar, kernel):
    """
    Given a core set of items and a grammar, recursively expand non-terminals
     into new items until there are no non-terminals left.

    :param grammar:
        A grammar, obviously.

    :param kernel:
        A :class:`set` of :class:`Item`s that make up the kernel of an item
        set.
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
                ).add(first)

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
        _Item(production, cursor=0, follow_set=follow_sets[production.name])
        for production in productions
    }


def _merge_items(a, b):
    if a.production != b.production or a.cursor != b.cursor:
        raise Exception('Item cores do not match')

    return _Item(
        a.production, a._cursor, set.union(a.follow_set, b.follow_set),
    )


def _merge_kernels(kernel_a, kernel_b):
    items_by_core_a = {
        (item.matched, item.expected): item for item in kernel_a
    }
    items_by_core_b = {
        (item.matched, item.expected): item for item in kernel_b
    }

    assert set(items_by_core_a) == set(items_by_core_b)

    return {
        _merge_items(items_by_core_a[core], items_by_core_b[core])
        for core in items_by_core_a
    }


def _build_item_set(grammar, kernel):
    return _ItemSet(kernel, _build_derived_items(grammar, kernel))


def _item_set_transitions(grammar, item_set):
    kernels = {}

    for item in item_set:
        if not item.expected:
            continue

        symbol, *rest = item.expected

        kernel = kernels.setdefault(symbol, set())
        kernel.add(_Item(item.production, item.cursor + 1, item.follow_set))

    return {
        symbol: frozenset(kernel)
        for symbol, kernel in kernels.items()
    }


def _kernel_core(kernel):
    return frozenset((item.matched, item.expected) for item in kernel)


def _build_transition_table(grammar, target):
    """
    Build the item sets, and map out the corresponding transitions for a
    grammar that accepts the given target.
    """
    starting_item = _Item(
        InternalProduction(START, {target, }), cursor=0, follow_set={EOF},
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
            kernel = _merge_kernels(item_sets[item_set_index].kernel, kernel)
            item_set = _build_item_set(grammar, kernel)
            item_sets[item_set_index] = item_set
            transitions[item_set_index] = _item_set_transitions(
                grammar, item_set
            )
        else:
            item_set_index = len(item_sets)
            item_set = _build_item_set(grammar, kernel)
            item_sets_by_core[_kernel_core(kernel)] = item_set_index
            item_sets.append(item_set)
            transitions.append(_item_set_transitions(grammar, item_set))

        # TODO items are queued in an order that is predictable in practice,
        # but technically non-deterministic.  This should have no effect when
        # building a parser for valid grammars, but may impact error messages
        # and testing.  Sort explicitly by first appearance of each terminal
        # to fix.
        kernel_queue.update(
            transitions[item_set_index][terminal]
            for terminal in transitions[item_set_index]
        )

    transitions = [
        {
            symbol: item_sets_by_core[_kernel_core(kernel)]
            for symbol, kernel in transition_map.items()
        }
        for transition_map in transitions
    ]
    return item_sets, transitions


def _build_shift_table(grammar, item_sets, item_set_transitions):
    """
    Returns a list of maps from terminal symbols to shift actions.

    A shift action is simply an index into the item_set array.
    """
    shifts = []
    for transitions in item_set_transitions:
        shifts.append({
            symbol: state
            for symbol, state in transitions.items()
            if grammar.is_terminal(symbol)
        })
    return shifts


def _build_goto_table(grammar, item_sets, item_set_transitions):
    """
    Returns a list of dictionaries mapping from non-terminal symbols to the
    state that should follow.

    The items in the list correspond to items in the list of item sets.
    """
    gotos = []
    for transitions in item_set_transitions:
        gotos.append({
            symbol: state
            for symbol, state in transitions.items()
            if grammar.is_nonterminal(symbol)
        })
    return gotos


def _build_reduction_table(grammar, item_sets, item_set_transitions):
    """
    Returns a list of dictionaries mapping from terminal symbols to reduce
    actions.

    Reduce actions are represented simply by a reference to a production.
    The items in the list of reduction dictionaries correspond to items in the
    list of item sets.
    """
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


def _build_accept_table(grammar, item_sets, items_set_transitions):
    return [
        any(
            item.name == START and not item.expected
            for item in item_set
        )
        for item_set in item_sets
    ]


def _check_shift_reduce_conflicts(shifts, reductions):
    """
    Check for conflicts between a shift table and a reduce table
    """
    for item_set_shifts, item_set_reductions in zip(shifts, reductions):
        if set.intersection(set(item_set_shifts), set(item_set_reductions)):
            raise ShiftReduceConflictError()


class _State(object):
    """
    An opaque reference type pointing to a state in a parse table.
    """
    __slots__ = {'_table', '_index'}

    def __init__(self, table, index):
        self._table = table
        self._index = index

    def __hash__(self):
        return hash(self._index)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self._table._item_sets[self._index] ==
            other._table._item_sets[self._index]
        )


class ParseTable(object):
    def __init__(self, grammar, target):
        item_sets, transitions = _build_transition_table(grammar, target)
        self._item_sets, self._transitions = item_sets, transitions

        self._reductions = _build_reduction_table(
            grammar, item_sets, transitions,
        )
        self._shifts = _build_shift_table(
            grammar, item_sets, transitions,
        )
        self._gotos = _build_goto_table(
            grammar, item_sets, transitions,
        )
        self._accepts = _build_accept_table(
            grammar, item_sets, transitions,
        )

        _check_shift_reduce_conflicts(self._shifts, self._reductions)

    def states(self):
        """
        Returns an iterator over states identifiers in the parse table.
        """
        return (_State(self, index) for index in range(len(self._item_sets)))

    def start_state(self):
        return _State(self, 0)

    def reductions(self, state):
        """
        Returns a dictionary mapping from terminal symbols to reduce actions.

        A reduce action is represented simply be a reference to a production.
        """
        return MappingProxyType(self._reductions[state._index])

    def shifts(self, state):
        """
        For the given state, returns a dictionary mapping from terminal symbols
        to shift actions.

        A shift action is simply an identifier for another state.
        """
        return MappingProxyType({
            terminal: _State(self, index)
            for terminal, index in self._shifts[state._index].items()
        })

    def gotos(self, state):
        """
        Returns a dictionary mapping from non terminal symbols to shift
        actions.
        """
        return MappingProxyType({
            nonterminal: _State(self, index)
            for nonterminal, index in self._gotos[state._index].items()
        })

    def accepts(self, state):
        """
        Returns True if and end-of-file token in the given state will result in
        the string being accepted.
        """
        return self._accepts[state._index]
