_START_SYMBOL = '_S' # object()


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

    def productions(self, name=None):
        if name is None:
            return set(self._productions)

        return {
            production for production in self._productions
            if production.name == name
        }


class Queue(object):
    def __init__(self, items):
        self._queued = list(items)
        self._all = set(items)

    def add(self, item):
        if item not in self._all:
            self._queued += item
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
        return self.pop()


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

    __slots__ = ('_production', '_cursor')

    def __init__(self, production, cursor=0):
        assert cursor <= len(production)

        # TODO should this be an identifier instead of a concrete object
        self._production = production
        self._cursor = cursor

    def __hash__(self):
        return (
            hash(self.production) ^
            hash(self.cursor)
        )

    def __eq__(self, other):
        return (
            self.production == other.production and
            self.cursor == other.cursor
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
        return tuple(self.production[:self.cursor])

    @property
    def expected(self):
        return tuple(self.production[self.cursor:])

    def __str__(self):
        return "{name} → {matched} • {expected}".format(
            name = self.name,
            matched=' '.join(str(symbol) for symbol in self.matched),
            expected=' '.join(str(symbol) for symbol in self.expected),
        )

    def __repr__(self):
        return '[' + str(self) + ']'

    def shift(self):
        if self.cursor >= len(self.production):
            raise Exception("out of bounds")

        return Item(self.production, cursor=self.cursor)


class ItemSet(object):

    def __init__(self, kernel, derived):
        self._kernel = kernel
        self._derived = derived

    @property
    def kernel(self):
        raise NotImplementedError()

    @property
    def items(self):
        return set.union(
            self._kernel,
            self._derived,
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

    def following(self):
        subsets = {}

        for item in self.items:
            if item.expected:
                n = item.expected[0]
                subsets.setdefault(n, set())
                subsets[n].update(shift(item))

        return set(subsets.items)

    def __eq__(self, other):
        return self.items == other.items


def _build_derived_items(grammar, kernel):
    symbols = set()
    queue = set()
    derived = set()

    def _queue_symbols_from_item(item):
        symbols.add(item.name)
        if item.expected:
            symbol = item.expected[0]
            if symbol not in symbols:
                queue.add(symbol)

    for item in kernel:
        _queue_symbols_from_item(item)
        
    while queue:
        for production in grammar.productions(queue.pop()):
            item = Item(production, 0)
            _queue_symbols_from_item(item)
            derived.add(item)

    return derived


def build_item_set(grammar, kernel):
    return ItemSet(kernel, _build_derived_items(grammar, kernel))


def item_set_transitions(grammar, item_set):
    kernels = {}

    for item in item_set.items:
        if item.expected:
            symbol = item.expected[0]
            kernel = kernels.setdefault(symbol, set())
            kernel.add(Item(item.production, item.cursor + 1))

    # TODO maybe it would make sense to return only the kernel as we have to
    # deduplicate the generated item sets.  Generating each set more than once
    # takes more work, and deduplicating item sets is more expensive than
    # kernels as well
    return {
        symbol: build_item_set(grammar, kernel)
        for symbol, kernel in kernels.items()
    }


def build_transition_table(grammar, target):
    '''Build the item sets, and map out the corresponding transitions for a
    grammar that accepts the given target.
    '''
    starting_item = Item(Production(_START_SYMBOL, {target,}))

    # A list of item sets.  Item sets are identified by index.  We initialise
    # it with a new item set with the start symbol as its kernel
    item_sets = [
        build_item_set(grammar, {starting_item})
    ]

    # A list, with items corresponding to the sets `item_sets`  of
    # dictionaries mapping from symbols to item set indexes
    transitions = []

    # We eagerly add item sets to the item set list and gradually work our way
    # through adding the corresponding transition dictionaries.  If we get to
    # processing the last item set in the list and no more item sets need to be
    # added, then we are done.
    while len(transitions) < len(item_sets):
        target_item_set = item_sets[len(transitions)]
        target_transitions = {}

        for symbol, item_set in item_set_transitions(grammar, target_item_set).items():
            # TODO complexity here could be much better
            if item_set not in item_sets:
                item_sets.append(item_set)

            target_transitions[symbol] = item_sets.index(item_set)

        transitions.append(target_transitions)

    return item_sets, transitions


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

    for rule in rules:
        has_first_symbol.setdefault(rule.name, set()).add(rule.symbols[0])

    # A map from symbols to the set of terminals which can appear as the first
    # terminal in a string that the symbol matches
    first_sets = {}

    for terminal in grammar.terminals:
        # TODO if this is needed it should be folded into the inner loop.
        # kept separate for now so that it's very clear what is happening
        first_sets[terminal] = {terminal}

        queue = list(has_first_symbol[terminal])

        # The set of non-terminals to which the terminal has been added.  This
        # is checked before adding more non-terminals to the queue so we do not
        # need to check if a terminal has already been added to the first set
        # when pulling an item off it.
        done = set()

        while queue:
            non_terminal = queue.pop()
            first_sets.setdefault(non_terminal, set()).add(terminal)
            # It is important to add the non-terminal to done before updating
            # the queue to avoid infinite loops on self-recursive symbols
            done.add(non_terminal)
            queue.add(set.difference(has_symbol_as_first[non_terminal], done))

    assert (
        set(first_sets) == set.union(grammar.terminals, grammar.non_terminals)
    )

    # item sets should contain only terminals
    assert not any(
        set.difference(item_set, grammar.terminals)
        for item_set in item_sets.values()
    )

    return first_sets


def build_follow_sets(grammar, *args):
    """Build a map from non-terminals to sets of terminals that can come
    immediately after them.
    """
    for non_terminal in grammar.non_terminals:
        pass

    for production in grammar.productions:
        for symbol in production.symbols:
            pass
            

def build_action_table(grammar, *args):
    '''
    :returns:
        A list of dictionaries mapping from terminals to parser actions.  The
        items in the list correspond to the grammar parse states.
    '''

    def _make_shift():
        def _shift(parser):
            parser.stack.push(state)
            parser.advance()
        return _shift

    def _make_reduce(rule):
        def _reduce(parser):
            parser.stack.pop(len(rule))
            parser.stack.push(gotos[rule.name])

        return _reduce


def build_goto_table(grammar, *args):
    '''
    :returns:
        A dictionary mapping from non-terminal identifiers to state identifiers
    '''
    pass


class ParserState(object):
    def __init__(self, parser, tokens):
        self._tokens = iter(tokens)
        self.advance()

    def peek(self):
        return self._current

    def advance(self):
        self._current = next(self._input)

    def shift(self):
        raise NotImplementedError()

    def reduce(self):
        raise NotImplementedError()


class Parser(object):
    def __init__(self, item_sets, actions, gotos):
        """
        :param item_sets:
            A list of :class:`ItemSet` instances.
        :param actions:
            A list of maps from terminal symbols to actions.  The items in the
            list correspond to states in the item set list.  An action is TODO
        :param gotos:
            A list of map from non-terminal symbols to state indices.  The
            items in the list correspond to states in the item set list, as do
            the indices in the maps.
        """
        # TODO figure out if it would make more sense to build these in the
        # constructor from the grammar
        self._item_sets = item_sets
        self._actions = actions
        self._gotos = gotos

    def parse(self, tokens):
        state = ParserState(self, token)

        for token in tokens:
            action = self.action(token)
            action(state)


def parse(string, item_sets, actions, gotos):
    '''
    '''
    state_stack = [0]
    result_stack = []

    def _peek():
        return string[0]

    def _advance():
        string = string[1:]

    def _push(state):
        stack.append(state)

    def _pop(count):
        stack = stack[:-count]

    def _shift(state):
        result_stack.push(_peek())
        _advance()
        _push(state)

    def _reduce(rule):
        _pop(len(rule))
        _push(gotos[rule.name])

    while True:
        pass
        #symbol = _peek()
        #action = actions[_state()][symbol]
        #case action of:
        #    Shift state -> _shift(state)
        #    Reduce rule -> _reduce(rule)
        #    Accept -> return
        #    Nothing -> raise Exception()








