from typer.grammar.stellaParser import stellaParser as Stella


class StellaTypeError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class MissingMainError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__("ERROR_MISSING_MAIN")


class UndefinedVarError(StellaTypeError):
    def __init__(self, name) -> None:
        super().__init__(f"ERROR_UNDEFINED_VARIABLE\n{name}")


class UnexpectedTypeError(StellaTypeError):
    def __init__(self, expected_type, actual_type) -> None:
        super().__init__(f"ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION\nExpected: {expected_type}\nActual: {actual_type}")


class NotFunctionError(StellaTypeError):
    def __init__(self, expression: Stella.ExprContext) -> None:
        super().__init__(f"ERROR_NOT_A_FUNCTION\n{expression.start}")


class UnexpectedLambdaError(StellaTypeError):
    def __init__(self, expected_type) -> None:
        super().__init__(f"ERROR_UNEXPECTED_LAMBDA\nGot lambda while expecting {expected_type}")


class AmbiguousListTypeError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__(f"ERROR_AMBIGUOUS_LIST\nMissing list type context")


class NotRecordError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__("ERROR_NOT_A_RECORD")


class TupleIndexOutOfBoundsError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__("ERROR_TUPLE_INDEX_OUT_OF_BOUNDS")


class UnexpectedFieldAccessError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__("ERROR_UNEXPECTED_FIELD_ACCESS")
        

class UnexpectedListError(StellaTypeError):
    def __init__(self, expected_type) -> None:
        super().__init__(f"ERROR_UNEXPECTED_LIST\nExpected: {expected_type}")


class UnexpectedRecordError(StellaTypeError):
    def __init__(self, expected_type) -> None:
        super().__init__(f"ERROR_UNEXPECTED_RECORD\nExpected: {expected_type}")


class UnexpectedTupleError(StellaTypeError):
    def __init__(self, expected_type) -> None:
        super().__init__(f"ERROR_UNEXPECTED_TUPLE\nExpected: {expected_type}")


class IncorrectNumberOfArgumentsError(StellaTypeError):
    def __init__(self, expected_number: int, actual_number: int) -> None:
        super().__init__(f"ERROR_INCORRECT_NUMBER_OF_ARGUMENTS\nExpected: {expected_number}\nActual: {actual_number}")


class UnexpectedTypeForParameterError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__("ERROR_UNEXPECTED_TYPE_FOR_PARAMETER")
