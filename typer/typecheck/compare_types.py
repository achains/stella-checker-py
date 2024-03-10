from typer.grammar.stellaParser import stellaParser as Stella


def compare_types(lhs: Stella.StellatypeContext, rhs: Stella.StellatypeContext):
    if type(lhs) is not type(rhs):
        return False
