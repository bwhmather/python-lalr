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
    pass
