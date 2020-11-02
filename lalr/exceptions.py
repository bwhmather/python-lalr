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
        self, message, *, lookahead_token, valid_shifts, valid_reductions
    ):
        super(ParseError, self).__init__(message)
        self.lookahead_token = lookahead_token
        self.valid_shifts = valid_shifts
        self.valid_reductions = valid_reductions
