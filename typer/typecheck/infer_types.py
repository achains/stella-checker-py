from typing import Tuple

from typer.typecheck.type_error import *
from typer.typecheck.type_map import TypeMap


def infer_types(program_context: Stella.ProgramContext):
    program_declarations = program_context.decls
    fun_declarations: Tuple[Stella.DeclFunContext] = tuple(filter(lambda d: isinstance(d, Stella.DeclFunContext), program_declarations))

    scope_types = TypeMap()
    for fun_decl in fun_declarations:
        fun_type = Stella.TypeFunContext(fun_decl.parser, fun_decl)
        fun_type.paramTypes = [p.paramType for p in fun_decl.paramDecls]
        fun_type.returnType = fun_decl.returnType
        scope_types.insert(fun_decl.StellaIdent().symbol, fun_type)

    if not any(map(lambda ident: ident.text == "main", scope_types.context[0].keys())):
        raise MissingMainError()

    for fun_decl in fun_declarations:
        infer_expression_type(fun_decl, scope_types)


def check_inferred_type(infer_function):
    def infer_type(expression: Stella.ExprContext, scope_types: TypeMap,
                   expected_type: Stella.StellatypeContext = None):
        actual_type = infer_function(expression, scope_types, expected_type)
        if expected_type and not isinstance(actual_type, type(expected_type)):
            raise UnexpectedTypeError(type(expected_type), type(actual_type))
        return actual_type
    return infer_type


@check_inferred_type
def infer_expression_type(expression: Stella.ExprContext,
                          scope_types: TypeMap,
                          expected_type: Stella.StellatypeContext = None):
    match expression:
        # Trivial types
        case Stella.ConstFalseContext() as false_ctx:
            return _infer_bool(false_ctx, scope_types, expected_type)
        case Stella.ConstTrueContext() as true_ctx:
            return _infer_bool(true_ctx, scope_types, expected_type)
        case Stella.ConstIntContext() as int_ctx:
            return _infer_int(int_ctx, scope_types, expected_type)
        # Integer built-ins
        case Stella.SuccContext() as succ_ctx:
            return _infer_nat_increment(succ_ctx, scope_types, expected_type)
        case Stella.PredContext() as pred_ctx:
            return _infer_nat_increment(pred_ctx, scope_types, expected_type)
        case Stella.IsZeroContext() as is_zero_ctx:
            infer_expression_type(is_zero_ctx.n, scope_types, Stella.TypeNatContext(is_zero_ctx.parser, is_zero_ctx))
            return Stella.TypeBoolContext(is_zero_ctx.parser, is_zero_ctx)
        # If expression
        case Stella.IfContext() as if_ctx:
            return _infer_if(if_ctx, scope_types, expected_type)
        # Variable
        case Stella.VarContext() as var_ctx:
            return scope_types.find(var_ctx.name)
        # Abstraction
        case Stella.AbstractionContext() as abs_ctx:
            return _infer_abstraction(abs_ctx, scope_types, expected_type)
        case Stella.ApplicationContext() as app_ctx:
            return _infer_application(app_ctx, scope_types, expected_type)
        # Parenthesised Expression
        case Stella.ParenthesisedExprContext() as parens_ctx:
            return infer_expression_type(parens_ctx.expr_, scope_types, expected_type)
        # Semicolon
        case Stella.TerminatingSemicolonContext() as semicolon_ctx:
            return infer_expression_type(semicolon_ctx.expr_, scope_types, expected_type)
        # Let-binding
        case Stella.LetContext() as let_ctx:
            return _infer_let(let_ctx, scope_types, expected_type)
        # List
        case Stella.ListContext() as list_ctx:
            return _infer_list(list_ctx, scope_types, expected_type)
        case Stella.ConsListContext() as cons_list_ctx:
            return _infer_cons_list(cons_list_ctx, scope_types, expected_type)
        # Function declaration
        case Stella.DeclFunContext() as fun_ctx:
            expected_return_type = scope_types.find(fun_ctx.StellaIdent().symbol).returnType
            function_scope = scope_types.nested_scope()
            for param_decl in fun_ctx.paramDecls:
                function_scope.insert(param_decl.name, param_decl.paramType)
            infer_expression_type(fun_ctx.returnExpr, function_scope, expected_type=expected_return_type)
        case _ as unexpected:
            print(unexpected.start)
            raise NotImplementedError


@check_inferred_type
def _infer_bool(expression: Stella.ConstFalseContext | Stella.ConstTrueContext, scope_types: TypeMap, expected_type: Stella.StellatypeContext = None):
    return Stella.TypeBoolContext(expression.parser, expression)


@check_inferred_type
def _infer_int(expression: Stella.ConstIntContext, scope_types: TypeMap, expected_type: Stella.StellatypeContext = None):
    return Stella.TypeNatContext(expression.parser, expression)


@check_inferred_type
def _infer_if(expression: Stella.IfContext, scope_types: TypeMap, expected_type: Stella.StellatypeContext = None):
    condition = infer_expression_type(expression.condition, scope_types, Stella.TypeBoolContext(expression.parser, expression))
    then_type = infer_expression_type(expression.thenExpr, scope_types, expected_type)
    else_type = infer_expression_type(expression.elseExpr, scope_types, expected_type)
    if not isinstance(then_type, type(else_type)):
        raise UnexpectedTypeError(type(then_type), type(else_type))
    return then_type


@check_inferred_type
def _infer_nat_increment(expression: Stella.SuccContext | Stella.PredContext, scope_types: TypeMap, expected_type: Stella.StellatypeContext = None):
    inner_type = infer_expression_type(expression.n, scope_types, Stella.TypeNatContext(expression.parser, expression))
    return inner_type


@check_inferred_type
def _infer_application(expression: Stella.ApplicationContext, scope_types: TypeMap, expected_type: Stella.StellatypeContext = None):
    fun_type = infer_expression_type(expression.fun, scope_types)
    if not isinstance(fun_type, Stella.TypeFunContext):
        raise NotFunctionError(expression)
    application_params = expression.args
    fun_param_types = fun_type.paramTypes

    if len(application_params) != len(fun_param_types):
        raise IncorrectNumberOfArgumentsError(len(fun_param_types), len(application_params))

    for i in range(len(application_params)):
        infer_expression_type(application_params[i], scope_types, expected_type=fun_param_types[i])

    return fun_type.returnType


@check_inferred_type
def _infer_abstraction(expression: Stella.AbstractionContext, scope_types: TypeMap, expected_type: Stella.StellatypeContext = None):
    if expected_type and not isinstance(expected_type, Stella.TypeFunContext):
        raise UnexpectedLambdaError(type(expected_type))

    return_type_scope = scope_types.nested_scope()
    for param_decl in expression.paramDecls:
        return_type_scope.insert(param_decl.StellaIdent().symbol, param_decl.paramType)

    return_type = infer_expression_type(expression.returnExpr, return_type_scope)

    abstraction_fun_type = Stella.TypeFunContext(expression.parser, expression)
    abstraction_fun_type.paramTypes = [param_decl.paramType for param_decl in expression.paramDecls]
    abstraction_fun_type.returnType = return_type

    return abstraction_fun_type


@check_inferred_type
def _infer_let(expression: Stella.LetContext, scope_types: TypeMap, expected_type: Stella.StellatypeContext = None):
    let_scope = scope_types.nested_scope()
    pattern_binding: Stella.PatternBindingContext
    for pattern_binding in expression.patternBindings:
        binding_token = pattern_binding.pat.StellaIdent().symbol
        binding_type = infer_expression_type(pattern_binding.rhs, scope_types)
        let_scope.insert(binding_token, binding_type)
    return infer_expression_type(expression.body, let_scope, expected_type)


@check_inferred_type
def _infer_list(expression: Stella.ListContext, scope_types: TypeMap, expected_type: Stella.StellatypeContext = None):
    if not expected_type:
        raise AmbiguousListTypeError
    if not isinstance(expected_type, Stella.TypeListContext):
        raise UnexpectedListError(expected_type)
    for element_expr in expression.exprs:
        infer_expression_type(element_expr, scope_types, expected_type.type_)
    return expected_type


@check_inferred_type
def _infer_cons_list(expression: Stella.ConsListContext, scope_types: TypeMap, expected_type: Stella.StellatypeContext = None):
    if not expected_type:
        raise AmbiguousListTypeError
    if not isinstance(expected_type, Stella.TypeListContext):
        raise UnexpectedListError(expected_type)

    tail_list_type = infer_expression_type(expression.tail, scope_types, expected_type)
    head_type = infer_expression_type(expression.head, scope_types, tail_list_type.type_)
    return expected_type
