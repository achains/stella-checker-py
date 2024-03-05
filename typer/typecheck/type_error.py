class StellaTypeError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class MissingMainError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__("ERROR_MISSING_MAIN")


class UndefinedVarError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__("ERROR_UNDEFINED_VARIABLE")


class UnexpectedTypeError(StellaTypeError):
    def __init__(self, expected_type, actual_type) -> None:
        super().__init__(f"ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION\nExpected: {expected_type}\nActual: {actual_type}")


class NotFunctionError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__("ERROR_NOT_A_FUNCTION")


class UnexpectedTypeForParameterError(StellaTypeError):
    def __init__(self) -> None:
        super().__init__("ERROR_UNEXPECTED_TYPE_FOR_PARAMETER")
