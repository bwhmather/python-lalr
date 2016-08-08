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
        result_stack = []

        def _top():
            return state_stack[-1]

        def _advance():
            nonlocal lookahead
            try:
                lookahead = next(tokens)
            except StopIteration:
                lookahead = EOF

        _advance()
        while True:
            if lookahead == EOF and self._parse_table.accepts(_top()):
                break

            # Shift
            elif lookahead in self._parse_table.shifts(_top()):
                state_stack.append(
                    self._parse_table.shifts(_top())[lookahead],
                )

                result_stack.append(lookahead)

                _advance()

            # Reduce
            elif lookahead in self._parse_table.reductions(_top()):
                production = self._parse_table.reductions(_top())[lookahead]

                # Pull the results for each of the symbols making up the
                # production from the stack.
                assert len(result_stack) >= len(production)
                values = tuple(result_stack[-len(production):])
                del result_stack[-len(production):]

                # value = production.action(values)  # TODO
                value = (production.name, values)
                result_stack.append(value)

                # Remove the intermediate states that have been added since the
                # production started.  These are no longer needed as they
                # cannot now appear just before the start of a new symbol.
                assert len(state_stack) > len(production)
                del state_stack[-len(production):]

                # The top of the stack is now a state that contains an item
                # with the cursor just before the symbol that was just parsed.
                # From here we essentially do a shift, but with a non-terminal
                # not a terminal.
                state_stack.append(
                    self._parse_table.gotos(_top())[production.name],
                )

            else:
                raise ParseError("unexpected token %r" % lookahead)

        assert len(result_stack) == 1
        return result_stack[0]
