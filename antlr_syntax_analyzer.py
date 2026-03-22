from dataclasses import dataclass
from typing import List

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from antlr_generated.antlr.FunctionDefLexer import FunctionDefLexer
from antlr_generated.antlr.FunctionDefParser import FunctionDefParser
from syntax_analyzer import ParseResult, SyntaxError


@dataclass
class _RawError:
    line: int
    column_start: int
    column_end: int
    unexpected_lexeme: str
    message: str


class _CollectingErrorListener(ErrorListener):
    def __init__(self) -> None:
        super().__init__()
        self.errors: List[_RawError] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):  # noqa: N802
        lexeme = "<конец файла>"
        end_col = column + 1

        if offendingSymbol is not None and getattr(offendingSymbol, "text", None):
            text = offendingSymbol.text
            if text != "<EOF>":
                lexeme = text
                end_col = column + len(text)

        message = msg or "Синтаксическая ошибка"

        self.errors.append(
            _RawError(
                line=max(1, int(line)),
                column_start=max(1, int(column) + 1),
                column_end=max(1, int(end_col)),
                unexpected_lexeme=lexeme,
                message=message,
            )
        )


class AntlrSyntaxAnalyzer:
    """ANTLR-based syntax analyzer for the function-definition grammar."""

    def analyze_text(self, text: str) -> ParseResult:
        result = ParseResult(success=True, errors=[], recovered_errors=0)

        if not text.strip():
            return result

        lexer_listener = _CollectingErrorListener()
        parser_listener = _CollectingErrorListener()

        input_stream = InputStream(text)
        lexer = FunctionDefLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(lexer_listener)

        token_stream = CommonTokenStream(lexer)
        parser = FunctionDefParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(parser_listener)

        parser.start()

        merged = lexer_listener.errors + parser_listener.errors
        merged.sort(key=lambda item: (item.line, item.column_start, item.message))

        dedup: set[tuple[int, int, str]] = set()
        for err in merged:
            key = (err.line, err.column_start, err.message)
            if key in dedup:
                continue
            dedup.add(key)
            result.errors.append(
                SyntaxError(
                    code=-1,
                    error_type="синтаксическая ошибка",
                    unexpected_lexeme=err.unexpected_lexeme,
                    expected="",
                    line=err.line,
                    column_start=err.column_start,
                    column_end=err.column_end,
                    message=err.message,
                )
            )

        result.recovered_errors = len(result.errors)
        result.success = len(result.errors) == 0
        return result
