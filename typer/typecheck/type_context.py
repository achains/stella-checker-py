import copy

from typing import List, Dict

from typer.grammar.stellaParser import stellaParser


class TypeContext:
    def __init__(self):
        self.__context: List[Dict[stellaParser.StellaIdent, stellaParser.StellatypeContext]] = [dict()]

    def insert(self, token: stellaParser.StellaIdent, ctx: stellaParser.StellatypeContext):
        self.__context[-1][token] = ctx

    def find(self, token: stellaParser.StellaIdent):
        for context in self.__context[::-1]:
            for ident, ident_type in context.items():
                if str(token) == str(ident):
                    return ident_type
                else:
                    try:
                        if token.text == ident.text:
                            return ident_type
                    except AttributeError:
                        pass
        return None

    @property
    def context(self):
        return self.__context

    def nested_scope(self) -> 'TypeContext':
        new_context = TypeContext()
        new_context.__context = [dict() for _ in range(len(self.__context) + 1)]
        for i in range(len(self.__context)):
            new_context.__context[i] = copy.copy(self.__context[i])
        return new_context
