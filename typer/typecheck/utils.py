from typer.grammar.stellaParser import stellaParser
from typing import Type


def make_function_type(parser: stellaParser, fun_decl: stellaParser.DeclFunContext) -> stellaParser.TypeFunContext:
    type_fun = stellaParser.TypeFunContext(parser, fun_decl)
    type_fun.returnType = fun_decl.returnType
    type_fun.paramTypes = fun_decl.paramDecls
    return type_fun


def make_context(parser: stellaParser, ctx_type: Type[stellaParser.StellatypeContext]) -> stellaParser.StellatypeContext:
    dummy_ctx = stellaParser.StellatypeContext(parser)
    return ctx_type(parser, dummy_ctx)
