from typer.typecheck.type_error import *
from typer.grammar.stellaParser import stellaParser as Stella


def compare_types(expected: Stella.StellatypeContext, actual: Stella.StellatypeContext):
    if type(expected) is not type(actual):
        match actual:
            case Stella.TypeFunContext():
                raise UnexpectedLambdaError(expected)
            case Stella.TypeTupleContext():
                raise UnexpectedTupleError(expected)
            case Stella.TypeRecordContext():
                raise UnexpectedRecordError(expected)
            case Stella.TypeListContext():
                raise UnexpectedListError(expected)
            case _:
                raise UnexpectedTypeError(expected, actual)
    elif isinstance(expected, Stella.TypeListContext):
        return compare_types(expected.type_, actual.type_)
    return True
