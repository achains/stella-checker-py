import sys

from antlr4 import InputStream, CommonTokenStream
from typer.grammar.stellaLexer import stellaLexer
from typer.grammar.stellaParser import stellaParser

from typer import TypeChecker
from typer.typecheck.type_error import StellaTypeError


def check_program_types(program_source: str):
    input_stream = InputStream(program_source)
    lexer = stellaLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = stellaParser(token_stream)

    type_checker = TypeChecker(parser.program())

    try:
        type_checker.check_program_types()
    except StellaTypeError as e:
        print(e.message)
        return False


def main(*args, **kwargs):
    if len(sys.argv) < 2:
        raise RuntimeError("Usage: typer <file_name>")

    file_path = sys.argv[1]
    with open(file_path, "r") as f:
        return check_program_types(f.read())


if __name__ == "__main__":
    main()
