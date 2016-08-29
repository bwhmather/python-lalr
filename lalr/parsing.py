from lalr.exceptions import ParseError
from lalr.constants import EOF


def parse(parse_table, tokens, action):
    """

    :param tokens:
        An iterable of :class:`Token` objects.
    """
    tokens = iter(tokens)
    lookahead = None

    state_stack = [parse_table.start_state()]
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
        if lookahead == EOF and parse_table.accepts(_top()):
            break

        # Shift
        elif lookahead in parse_table.shifts(_top()):
            state_stack.append(
                parse_table.shifts(_top())[lookahead],
            )

            result_stack.append(lookahead)

            _advance()

        # Reduce
        elif lookahead in parse_table.reductions(_top()):
            production = parse_table.reductions(_top())[lookahead]

            # Pull the results for each of the symbols making up the production
            # from the stack.
            assert len(result_stack) >= len(production)
            values = tuple(result_stack[-len(production):])
            del result_stack[-len(production):]

            value = action(production, *values)
            result_stack.append(value)

            # Remove the intermediate states that have been added since the
            # production started.  These are no longer needed as they cannot
            # now appear just before the start of a new symbol.
            assert len(state_stack) > len(production)
            del state_stack[-len(production):]

            # The top of the stack is now a state that contains an item with
            # the cursor just before the symbol that was just parsed.  From
            # here we essentially do a shift, but with a non-terminal not a
            # terminal.
            state_stack.append(
                parse_table.gotos(_top())[production.name],
            )

        else:
            raise ParseError("unexpected token %r" % lookahead)

    assert len(result_stack) == 1
    return result_stack[0]
