from typer.grammar.stellaParser import stellaParser as Stella
from typer.typecheck.type_error import UnexpectedPatternForTypeError, NonExhaustiveMatchError


def create_case_type_getter(match_expression: Stella.StellatypeContext, case_map):
    match match_expression:
        case Stella.TypeSumContext():
            return lambda pattern: case_map[type(pattern)]
        case Stella.TypeVariantContext():
            return lambda pattern: case_map[pattern.label.text]


def exhaustive_check(match_expression: Stella.StellatypeContext, match_cases: list[Stella.MatchCaseContext]) -> dict:
    match match_expression:
        case Stella.TypeSumContext() as sum_type:
            return _check_match_sum_type(sum_type, match_cases)
        case Stella.TypeVariantContext() as variant_type:
            return _check_match_variant_type(variant_type, match_cases)
        case _:
            raise NotImplementedError(f"Pattern matching for {type(match_expression)}")


def _check_match_sum_type(match_expression: Stella.TypeSumContext, match_cases: list[Stella.MatchCaseContext]):
    sum_type_cases = {Stella.PatternInlContext: match_expression.left, Stella.PatternInrContext: match_expression.right}

    actual_cases = set()
    for pattern in map(lambda c: c.pattern_, match_cases):
        if type(pattern) not in sum_type_cases:
            raise UnexpectedPatternForTypeError(type(pattern), Stella.TypeSumContext)
        actual_cases.add(type(pattern))

    if actual_cases != set(sum_type_cases.keys()):
        raise NonExhaustiveMatchError

    return sum_type_cases


def _check_match_variant_type(variant_type: Stella.TypeVariantContext, match_cases: list[Stella.MatchCaseContext]):
    variant_type_cases = {field.label.text: field.type_ for field in variant_type.fieldTypes}

    actual_cases = set()
    for pattern in map(lambda c: c.pattern_, match_cases):
        if not isinstance(pattern, Stella.PatternVariantContext):
            raise UnexpectedPatternForTypeError(pattern, Stella.TypeVariantContext)
        if pattern.label.text not in variant_type_cases:
            raise UnexpectedPatternForTypeError(pattern.label.text, Stella.TypeVariantContext)
        actual_cases.add(pattern.label.text)

    if actual_cases != set(variant_type_cases.keys()):
        raise NonExhaustiveMatchError

    return variant_type_cases
