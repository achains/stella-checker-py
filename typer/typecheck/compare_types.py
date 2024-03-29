from typer.typecheck.type_error import *
from typer.grammar.stellaParser import stellaParser as Stella


def unwind_parens(parens_type: Stella.StellatypeContext):
    while isinstance(parens_type, Stella.TypeParensContext):
        parens_type = parens_type.type_
    return parens_type


def compare_types(expected: Stella.StellatypeContext, actual: Stella.StellatypeContext):
    if not expected:
        return True
    expected = unwind_parens(expected)
    actual = unwind_parens(actual)
    if type(expected) is not type(actual):
        match expected:
            case Stella.TypeFunContext():
                raise UnexpectedLambdaError(actual)
            case Stella.TypeTupleContext():
                raise UnexpectedTupleError(actual)
            case Stella.TypeRecordContext():
                raise UnexpectedRecordError(actual)
            case Stella.TypeListContext():
                raise UnexpectedListError(actual)
            case _:
                raise UnexpectedTypeError(type(expected), type(actual))
    elif isinstance(expected, Stella.TypeListContext):
        return compare_types(expected.type_, actual.type_)
    elif isinstance(expected, Stella.TypeTupleContext):
        if len(expected.types) != len(actual.types):
            raise UnexpectedTupleLengthError(len(expected.types), len(actual.types))
        for expected_type, actual_type in zip(expected.types, actual.types):
            compare_types(expected_type, actual_type)
    elif isinstance(expected, Stella.TypeRecordContext):
        if len(expected.fieldTypes) < len(actual.fieldTypes):
            raise UnexpectedRecordFieldsError
        if len(expected.fieldTypes) > len(actual.fieldTypes):
            raise MissingRecordFieldsError
        for expected_field, actual_field in zip(expected.fieldTypes, actual.fieldTypes):
            try:
                compare_types(expected_field, actual_field)
            except StellaTypeError:
                raise UnexpectedRecordFieldsError
    elif isinstance(expected, Stella.TypeParensContext):
        return compare_types(expected.type_, actual.type_)
    return True
