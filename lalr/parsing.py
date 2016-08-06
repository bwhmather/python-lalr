from lalr.exceptions import ParseError
from lalr.grammar import Grammar
from lalr.analysis import ParseTable, _build_transition_table, EOF


class Parser(object):
    def __init__(self, productions, target):
        grammar = Grammar(productions)

        item_sets, transitions = _build_transition_table(grammar, target)

        self._parse_table = ParseTable(grammar, target)

    def parse(self, tokens):
        tokens = iter(tokens)
        lookahead = None

        state_stack = [self._parse_table.start_state()]

        def _top():
            return state_stack[-1]

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
            print(state_stack)
            if lookahead == EOF and self._parse_table.accepts(_top()):
                break

            # Shift
            elif lookahead in self._parse_table.shifts(_top()):
                next_state = self._parse_table.shifts(_top())[lookahead]
                _push(next_state)
                _advance()

            # Reduce
            elif lookahead in self._parse_table.reductions(_top()):
                production = self._parse_table.reductions(_top())[lookahead]
                _pop(len(production))
                _push(self._parse_table.gotos(_top())[production.name])

            else:
                raise ParseError("unexpected token %r" % lookahead)
