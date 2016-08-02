from lalr.grammar import Grammar
from lalr.analysis import build_transition_table, EOF, START_SYMBOL
from lalr.exceptions import (
    ReduceReduceConflictError, ShiftReduceConflictError, ParseError,
)


def build_shift_table(grammar, item_sets, item_set_transitions):
    '''Returns a list of maps from terminal symbols to shift actions.

    A shift action is simply an index into the item_set array.
    '''
    shifts = []
    for transitions in item_set_transitions:
        shifts.append({
            symbol: state
            for symbol, state in transitions.items()
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
            for symbol, state in transitions.items()
            if grammar.is_nonterminal(symbol)
        })
    return gotos


def build_reduction_table(grammar, item_sets, item_set_transitions):
    '''Returns a list of dictionaries mapping from terminal symbols to reduce
    actions.

    Reduce actions are represented simply by a reference to a production.
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


def build_accept_table(grammar, item_sets, items_set_transitions):
    return [
        any(
            item.name == START_SYMBOL and not item.expected
            for item in item_set
        )
        for item_set in item_sets
    ]


def check_shift_reduce_conflicts(shifts, reductions):
    '''Check for conflicts between a shift table and a reduce table
    '''
    for item_set_shifts, item_set_reductions in zip(shifts, reductions):
        if set.intersection(set(item_set_shifts), set(item_set_reductions)):
            raise ShiftReduceConflictError()


class Parser(object):
    def __init__(self, productions, target):
        grammar = Grammar(productions)

        item_sets, transitions = build_transition_table(grammar, target)

        self._shifts = build_shift_table(
            grammar, item_sets, transitions
        )

        self._gotos = build_goto_table(
            grammar, item_sets, transitions
        )

        self._reductions = build_reduction_table(
            grammar, item_sets, transitions
        )

        self._accepts = build_accept_table(
            grammar, item_sets, transitions
        )

    def parse(self, tokens):
        tokens = iter(tokens)
        lookahead = None

        state_stack = [0]
        result_stack = []

        def _peek():
            return lookahead

        def _advance():
            nonlocal lookahead
            try:
                lookahead = next(tokens)
            except StopIteration:
                lookahead = EOF

        def _push(state):
            state_stack.append(state)

        def _pop(count):
            result = tuple(state_stack[-count:])
            del state_stack[-count:]
            return result

        _advance()
        while True:
            this_state = state_stack[-1]

            if lookahead == EOF and self._accepts[this_state]:
                break

            # Shift
            elif lookahead in self._shifts[this_state]:
                result_stack.append(lookahead)
                next_state = self._shifts[this_state][lookahead]
                _push(next_state)
                _advance()

            # Reduce
            elif lookahead in self._reductions[this_state]:
                production = self._reductions[this_state][lookahead]
                _pop(len(production))
                _push(self._gotos[state_stack[-1]][production.name])

            else:
                raise ParseError("unexpected token %r" % lookahead)
