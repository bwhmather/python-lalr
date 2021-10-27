class CompilationError(Exception):
    pass


class ProductionSpecParseError(CompilationError):
    pass


class ConflictError(CompilationError):
    pass


class ShiftReduceConflictError(ConflictError):
    pass


class ReduceReduceConflictError(ConflictError):
    pass


class ParseError(Exception):
    def __init__(
        self, message, *, lookahead_token, expected_symbols
    ):
        super(ParseError, self).__init__(message)
        self.lookahead_token = lookahead_token
        self.expected_symbols = expected_symbols
