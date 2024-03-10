import copy

from typing import List, Dict

from typer.grammar.stellaParser import stellaParser

from typer.typecheck.type_error import UndefinedVarError


class TypeMap:
    def __init__(self):
        self.__context: List[Dict[stellaParser.StellaIdent, stellaParser.StellatypeContext]] = [dict()]

    def insert(self, token: stellaParser.StellaIdent, ctx: stellaParser.StellatypeContext):
        self.__context[-1][token] = ctx

    def find(self, token: stellaParser.StellaIdent):
        for context in self.__context[::-1]:
            for ident, ident_type in context.items():
                if token.text == ident.text:
                    return ident_type
        raise UndefinedVarError(token.text)

    @property
    def context(self):
        return self.__context

    def nested_scope(self) -> 'TypeMap':
        new_context = TypeMap()
        new_context.__context = [dict() for _ in range(len(self.__context) + 1)]
        for i in range(len(self.__context)):
            new_context.__context[i] = copy.copy(self.__context[i])
        return new_context
