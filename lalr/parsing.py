from lalr.constants import EOF
from lalr.exceptions import ParseError


def _or_list(values):
    if len(values) > 1:
        return ", ".join(values[:-1]) + ' or ' + values[-1]
    else:
        return values[0]


def _default_token_symbol(token):
    return token


def _default_token_value(token):
    return token


def parse(
    parse_table, tokens, *, action,
    token_symbol=_default_token_symbol,
    token_value=_default_token_value,
):
    """
    The parser automaton loop.  This is an internal function.

    :param tokens:
        An iterable of token objects.  The token type is defined by the caller.
        If tokens are anything other than a string, the caller will most likely
        want to override the `token_symbol` and `token_value` functions.

    :param action:
        A callable that will be invoked after each reduce with a reference to
        the matched production followed by the computed value of each matched
        symbol within the production.

    :param token_symbol:
        An optional callable that takes a token and returns a string
        identifying the symbol that the token represents.  The default
        implementation returns the token, meaning that the input sequence must
        be an iterable of strings.

    :param token_value:
        An optional callable that takes a token and returns the value that
        should be pushed onto the result stack when the token is shifted.  The
        default implementation just returns the token.
    """
    tokens = iter(tokens)
    lookahead_token = None
    lookahead_symbol = None
    lookahead_value = None

    state_stack = [parse_table.start_state()]
    result_stack = []

    def _top():
        return state_stack[-1]

    def _advance():
        try:
            token = next(tokens)
        except StopIteration:
            token, symbol, value = None, EOF, None
        else:
            symbol, value = token_symbol(token), token_value(token)

        # We modify the state variables at the end of the function to avoid
        # partially clobbering them as a result of an error in either of the
        # token lookup functions.
        nonlocal lookahead_token, lookahead_symbol, lookahead_value
        lookahead_token, lookahead_symbol, lookahead_value = (
            token, symbol, value,
        )

    _advance()
    while True:
        if lookahead_symbol == EOF and parse_table.accepts(_top()):
            break

        # Shift
        elif lookahead_symbol in parse_table.shifts(_top()):
            state_stack.append(
                parse_table.shifts(_top())[lookahead_symbol],
            )

            result_stack.append(lookahead_value)

            _advance()

        # Reduce
        elif lookahead_symbol in parse_table.reductions(_top()):
            production = parse_table.reductions(_top())[lookahead_symbol]

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
            expected_tokens = {
                *parse_table.shifts(_top()),
                *parse_table.reductions(_top()),
            }
            expected_symbols = set()

            for token in expected_tokens:
                state_stack_ = list(state_stack)

                # Apply as many reductions as possible with the candidate
                # lookahead token.
                while True:
                    if token not in parse_table.reductions(state_stack_[-1]):
                        break

                    if token == EOF:
                        break

                    production = parse_table.reductions(state_stack_[-1])[token]

                    del state_stack_[-len(production):]
                    state_stack_.append(
                        parse_table.gotos(state_stack_[-1])[production.name]
                    )

                # Find all symbols that can follow it at the same level of
                # abstraction.
                for item in parse_table.item_set(state_stack_[-1]).kernel:
                    if not item.expected:
                        continue
                    expected_symbols.add(item.expected[0])

            if expected_symbols:
                message = (
                    f"expected {_or_list(sorted(expected_symbols))} "
                    f"before {lookahead_symbol if lookahead_symbol is not EOF else 'EOF'}"
                )
            else:
                message = f"expected EOF instead of {lookahead_symbol}"

            raise ParseError(
                message,
                lookahead_token=lookahead_token,
                expected_symbols=expected_symbols,
            )

    assert len(result_stack) == 1
    return result_stack[0]
