from typing import Type

from antlr4.Token import CommonToken

from typer.grammar.stellaParser import stellaParser
from typer.typecheck.type_error import *
from typer.typecheck.utils import make_function_type, make_context

__all__ = ["TypeChecker"]


class TypeContext:
    pass


class TypeChecker:
    def __init__(self, program_context: stellaParser.ProgramContext):
        self.__program_context = program_context
        self.__make_function_type = lambda fun_decl: make_function_type(self.__program_context.parser, fun_decl)
        self.__make_context = lambda context_type: make_context(self.__program_context.parser, context_type)

    def check_program_types(self):
        program_declarations = self.__program_context.decls
        function_declarations = list(filter(lambda d: isinstance(d, stellaParser.DeclFunContext), program_declarations))
        type_context = TypeContext()

        fun_decl: stellaParser.DeclFunContext
        for fun_decl in function_declarations:
            type_context.insert(fun_decl.StellaIdent(), self.__make_function_type(fun_decl))

        if not self.has_main(type_context):
            raise MissingMainError()

        fun_decl: stellaParser.DeclFunContext
        for fun_decl in function_declarations:
            self.check_top_level_fun(fun_decl, type_context)

    def check_top_level_fun(self, fun_decl: stellaParser.DeclFunContext, type_context: TypeContext):
        body_context = type_context.nested_scope()

        param_decl: stellaParser.ParamDeclContext
        for param_decl in fun_decl.paramDecls:
            body_context.insert(param_decl.StellaIdent(), param_decl.paramType)

        expected_return_type = fun_decl.returnType
        actual_return_type = self.infer_expression_type(fun_decl.returnExpr, body_context)
        if not isinstance(actual_return_type, type(expected_return_type)):
            raise UnexpectedTypeError(type(expected_return_type), type(actual_return_type))

    def infer_expression_type(self, expr: stellaParser.ExprContext,
                              type_context: TypeContext) -> stellaParser.StellatypeContext:
        match expr:
            case stellaParser.ConstFalseContext():
                return self.__make_context(stellaParser.TypeBoolContext)
            case stellaParser.ConstTrueContext():
                return self.__make_context(stellaParser.TypeBoolContext)
            case stellaParser.ConstIntContext():
                return self.__make_context(stellaParser.TypeNatContext)
            case stellaParser.IfContext() as if_ctx:
                condition_type = self.infer_expression_type(if_ctx.condition, type_context)
                if not isinstance(condition_type, stellaParser.TypeBoolContext):
                    raise UnexpectedTypeError(stellaParser.TypeBoolContext, type(condition_type))
                then_type = self.infer_expression_type(if_ctx.thenExpr, type_context)
                else_type = self.infer_expression_type(if_ctx.elseExpr, type_context)
                if type(then_type) is not type(else_type):
                    raise UnexpectedTypeError(type(then_type), type(else_type))
                return then_type
            case stellaParser.IsZeroContext() as is_zero_ctx:
                inner_type = self.infer_expression_type(is_zero_ctx.n, type_context)
                if not isinstance(inner_type, stellaParser.TypeNatContext):
                    raise UnexpectedTypeError(stellaParser.TypeNatContext, inner_type)
                return self.__make_context(stellaParser.TypeBoolContext)
            case stellaParser.VarContext() as var_ctx:
                var_type = type_context.find(var_ctx.StellaIdent())
                if var_type is None:
                    raise UndefinedVarError
                return var_type
            case stellaParser.SuccContext() as succ_ctx:
                inner_type = self.infer_expression_type(succ_ctx.n, type_context)
                if not isinstance(inner_type, stellaParser.TypeNatContext):
                    raise UnexpectedTypeError(stellaParser.TypeNatContext, type(inner_type))
                return self.__make_context(stellaParser.TypeNatContext)
            case stellaParser.PredContext() as pred_ctx:
                inner_type = self.infer_expression_type(pred_ctx.n, type_context)
                if not isinstance(inner_type, stellaParser.TypeNatContext):
                    raise UnexpectedTypeError(stellaParser.TypeNatContext, inner_type)
                return self.__make_context(stellaParser.TypeNatContext)
            case stellaParser.ApplicationContext() as application_ctx:
                fun_type = self.infer_expression_type(application_ctx.fun, type_context)
                if not isinstance(fun_type, stellaParser.TypeFunContext):
                    raise NotFunctionError

                actual_param_types = [self.infer_expression_type(arg, type_context) for arg in application_ctx.args]
                expected_param_types = fun_type.paramTypes

                if len(actual_param_types) != len(expected_param_types):
                    raise RuntimeError("TODO: Number of arguments is different")

                for actual, expected in zip(actual_param_types, expected_param_types):
                    if not isinstance(actual, type(expected)):
                        raise UnexpectedTypeForParameterError()
                return fun_type.returnType
            case stellaParser.AbstractionContext() as abstraction_ctx:
                return_ctx = type_context.nested_scope()
                for param_decl in abstraction_ctx.paramDecls:
                    return_ctx.insert(param_decl.StellaIdent(), param_decl.paramType)

                return_type = self.infer_expression_type(abstraction_ctx.returnExpr, return_ctx)

                abstraction_fun_decl = stellaParser.DeclFunContext(self.__program_context.parser, abstraction_ctx)
                abstraction_fun_decl.paramDecls = abstraction_ctx.paramDecls
                abstraction_fun_decl.returnType = return_type
                return self.__make_function_type(abstraction_fun_decl)
            case stellaParser.ParenthesisedExprContext() as parens_ctx:
                return self.infer_expression_type(parens_ctx.expr_, type_context)
            case stellaParser.TerminatingSemicolonContext() as semicolon_ctx:
                return self.infer_expression_type(semicolon_ctx.expr_, type_context)
            case stellaParser.LetContext() as let_ctx:
                body = let_ctx.body
                pattern_binding: stellaParser.PatternBindingContext
                let_type_ctx = type_context.nested_scope()
                for pattern_binding in let_ctx.patternBindings:
                    binding_token = pattern_binding.pat.StellaIdent()
                    binding_type = self.infer_expression_type(pattern_binding.rhs, let_type_ctx)
                    let_type_ctx.insert(binding_token, binding_type)

                return self.infer_expression_type(body, let_type_ctx)
            case stellaParser.RecordContext() as record_ctx:
                record_type = stellaParser.TypeRecordContext(record_ctx.parser, record_ctx)
                for pattern_binding in record_ctx.bindings:
                    record_field_ctx = stellaParser.RecordFieldTypeContext(record_ctx.parser, record_type)
                    record_field_ctx.label = pattern_binding.name
                    record_field_ctx.type_ = self.infer_expression_type(pattern_binding.rhs, type_context)
                    record_type.fieldTypes.append(record_field_ctx)
                return record_type
            case stellaParser.DotRecordContext() as dot_record_ctx:
                record_type = self.infer_expression_type(dot_record_ctx.expr_, type_context)
                if not isinstance(record_type, stellaParser.TypeRecordContext):
                    raise NotRecordError

                record_type_map = TypeContext()
                for field_type in record_type.fieldTypes:
                    record_type_map.insert(field_type.label, field_type.type_)

                label_type = record_type_map.find(dot_record_ctx.label)
                if label_type is None:
                    raise UnexpectedFieldAccessError
                return label_type
            case stellaParser.TupleContext() as tuple_ctx:
                tuple_type = stellaParser.TypeTupleContext(tuple_ctx.parser, tuple_ctx)
                for tuple_expr in tuple_ctx.exprs:
                    tuple_type.types.append(self.infer_expression_type(tuple_expr, type_context))
                return tuple_type
            case stellaParser.DotTupleContext() as dot_tuple_ctx:
                tuple_type = self.infer_expression_type(dot_tuple_ctx.expr_, type_context)
                if not isinstance(tuple_type, stellaParser.TypeTupleContext):
                    raise UnexpectedTypeError(stellaParser.TypeTupleContext, type(tuple_type))
                int_index = int(dot_tuple_ctx.index.text)
                if int_index < 1 or int_index > len(tuple_type.types):
                    raise TupleIndexOutOfBoundsError
                return tuple_type.types[int_index - 1]
            case stellaParser.ListContext() as list_ctx:
                list_type = stellaParser.TypeListContext(list_ctx.parser, list_ctx)
                if len(list_ctx.exprs) == 0:
                    return list_type
                first_element_type = self.infer_expression_type(list_ctx.exprs[0], type_context)

            case stellaParser.AnnotationContext() as annotation_ctx:
                raise NotImplementedError("Annotation")
            case stellaParser.ConstUnitContext() as const_unit_ctx:
                raise NotImplementedError("Unit")
            case stellaParser.VariantContext() as variant_ctx:
                raise NotImplementedError("Variant")
            case _ as unexpected_context:
                print(type(unexpected_context))
                print(unexpected_context.start)
                raise NotImplementedError

    @staticmethod
    def has_main(type_context: TypeContext) -> bool:
        global_idents = type_context.context[0].keys()
        return 1 == len(list(filter(lambda ident: str(ident) == "main", global_idents)))
