from dataclasses import dataclass
import re
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

        # Lexer errors may not have offendingSymbol; extract bad symbol from message.
        bad_symbol = re.search(r"token recognition error at:\s*'([^']+)'", message)
        if bad_symbol is not None:
            lexeme = bad_symbol.group(1)
            end_col = column + len(lexeme)

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
    _TYPE_TOKENS = {"Int", "String", "Double", "Float", "Boolean"}

    _TOKEN_MESSAGE_MAP = {
        "val": "Ожидалось 'val'",
        ":": "Ожидалось ':'",
        "(": "Ожидалась '('",
        ")": "Ожидалась ')'",
        "->": "Ожидалась '->'",
        "=": "Ожидалось '='",
        "{": "Ожидалась '{'",
        "}": "Ожидалась '}'",
        ";": "Ожидалась ';' в конце выражения",
        ",": "Ожидалась ',' между параметрами",
        "<EOF>": "Неожиданные токены в конце выражения",
    }

    @staticmethod
    def _looks_like_val_typo(text: str) -> bool:
        candidate = (text or "").strip().lower()
        target = "val"

        if candidate == "vla":
            return True

        if abs(len(candidate) - len(target)) > 1:
            return False

        i = 0
        j = 0
        mismatches = 0
        while i < len(candidate) and j < len(target):
            if candidate[i] == target[j]:
                i += 1
                j += 1
                continue

            mismatches += 1
            if mismatches > 1:
                return False

            if len(candidate) == len(target):
                i += 1
                j += 1
            elif len(candidate) > len(target):
                i += 1
            else:
                j += 1

        if i < len(candidate) or j < len(target):
            mismatches += 1

        return mismatches <= 1

    @staticmethod
    def _clean_expected_token(token: str) -> str:
        cleaned = token.strip().strip("{}").strip()
        if cleaned.startswith("'") and cleaned.endswith("'") and len(cleaned) >= 2:
            cleaned = cleaned[1:-1]
        return cleaned

    def _parse_expected_tokens(self, expected_part: str) -> List[str]:
        part = (expected_part or "").strip()
        if not part:
            return []

        if part.startswith("{") and part.endswith("}"):
            tokens = [self._clean_expected_token(p) for p in part[1:-1].split(",")]
            return [t for t in tokens if t]

        token = self._clean_expected_token(part)
        return [token] if token else []

    def _message_from_expected(self, expected_tokens: List[str], unexpected_lexeme: str) -> str:
        if not expected_tokens:
            return "Синтаксическая ошибка"

        expected_set = set(expected_tokens)

        if expected_set.issuperset(self._TYPE_TOKENS) or any(
            token in self._TYPE_TOKENS for token in expected_tokens
        ):
            return "Ожидался тип (Int, String, Double, Float, Boolean)"

        expr_start = {"IDENT", "NUMBER", "("}
        if expr_start.issubset(expected_set) or ("IDENT" in expected_set and "NUMBER" in expected_set):
            return "Ожидалось число, идентификатор или '('"

        if "IDENT" in expected_set:
            if unexpected_lexeme == ":":
                return "Ожидалось имя функции"
            return "Ожидалось имя параметра"

        for token in expected_tokens:
            if token in self._TOKEN_MESSAGE_MAP:
                return self._TOKEN_MESSAGE_MAP[token]

        return "Синтаксическая ошибка"

    def _normalize_message(self, raw_message: str, unexpected_lexeme: str) -> str:
        message = (raw_message or "").strip()
        lower = message.lower()

        bad_symbol = re.search(r"token recognition error at:\s*'([^']+)'", message)
        if bad_symbol is not None:
            symbol = bad_symbol.group(1)
            return f"Недопустимый символ '{symbol}'"

        missing = re.search(r"missing\s+(.+?)\s+at\s+", message, flags=re.IGNORECASE)
        if missing is not None:
            token = self._clean_expected_token(missing.group(1))
            return self._message_from_expected([token], unexpected_lexeme)

        expecting = re.search(
            r"(?:extraneous|mismatched)\s+input\s+.+?\s+expecting\s+(.+)$",
            message,
            flags=re.IGNORECASE,
        )
        if expecting is not None:
            tokens = self._parse_expected_tokens(expecting.group(1))
            return self._message_from_expected(tokens, unexpected_lexeme)

        if "no viable alternative" in lower:
            if unexpected_lexeme in {"+", "-", "*", "/", "%"}:
                return "Ожидалось выражение после оператора"
            return "Синтаксическая ошибка"

        return "Синтаксическая ошибка"

    def _drop_cascade_errors(self, errors: List[_RawError]) -> List[_RawError]:
        if not errors:
            return errors

        result: List[_RawError] = []
        idx = 0
        while idx < len(errors):
            current = errors[idx]
            current_msg = current.message.lower()
            if (
                "missing 'val'" in current_msg
                and self._looks_like_val_typo(current.unexpected_lexeme)
                and idx + 1 < len(errors)
            ):
                nxt = errors[idx + 1]
                next_msg = nxt.message.lower()
                is_extraneous_colon = (
                    "extraneous input" in next_msg
                    and re.search(r"expecting\s*':'", next_msg) is not None
                )
                same_line_and_near = (
                    nxt.line == current.line
                    and nxt.column_start <= current.column_end + 2
                )

                if is_extraneous_colon and same_line_and_near:
                    result.append(current)
                    idx += 2
                    continue

            if "token recognition error" in current_msg and idx + 1 < len(errors):
                nxt = errors[idx + 1]
                next_msg = nxt.message.lower()
                is_missing_ident_at_colon = (
                    nxt.unexpected_lexeme == ":"
                    and (
                        re.search(r"missing\s+ident\s+at\s+':'", next_msg) is not None
                        or re.search(r"expecting\s+\{?\s*ident\s*\}?", next_msg) is not None
                    )
                )
                same_line_and_near = (
                    nxt.line == current.line
                    and nxt.column_start <= current.column_end + 2
                )

                if is_missing_ident_at_colon and same_line_and_near:
                    result.append(current)
                    idx += 2
                    continue

            if idx + 1 < len(errors):
                nxt = errors[idx + 1]
                next_msg = nxt.message.lower()
                is_param_missing_at_arrow = (
                    current.unexpected_lexeme == "->"
                    and "extraneous input" in current_msg
                    and re.search(r"expecting\s+\{[^}]*ident[^}]*\}", current_msg) is not None
                )
                is_followup_expecting_arrow = (
                    "mismatched input" in next_msg
                    and re.search(r"expecting\s+'->'", next_msg) is not None
                )
                same_or_next_line = nxt.line in {current.line, current.line + 1}

                if is_param_missing_at_arrow and is_followup_expecting_arrow and same_or_next_line:
                    result.append(current)
                    idx += 2
                    continue

            result.append(current)
            idx += 1

        return result

    @staticmethod
    def _has_missing_rparen_error(errors: List[_RawError]) -> bool:
        for err in errors:
            msg = (err.message or "").lower()
            if re.search(r"missing\s+'?\)'?", msg) is not None:
                return True
            if re.search(r"expecting\s+\{?\s*'\)'\s*\}?", msg) is not None:
                return True
        return False

    def _infer_missing_rparen_in_lambda_expr(self, token_stream: CommonTokenStream, errors: List[_RawError]) -> List[_RawError]:
        if self._has_missing_rparen_error(errors):
            return []

        tokens = [t for t in token_stream.tokens if getattr(t, "text", None) is not None]
        if not tokens:
            return []

        in_lambda_body = False
        in_expr = False
        paren_depth = 0

        for tok in tokens:
            text = tok.text

            if text == "{":
                in_lambda_body = True
                in_expr = False
                paren_depth = 0
                continue

            if not in_lambda_body:
                continue

            if not in_expr:
                if text == "->":
                    in_expr = True
                continue

            if text == "(":
                paren_depth += 1
                continue

            if text == ")":
                if paren_depth > 0:
                    paren_depth -= 1
                continue

            if text in {"}", ";", "<EOF>"}:
                if paren_depth > 0:
                    line = max(1, int(tok.line))
                    col_start = max(1, int(tok.column) + 1)
                    lexeme = "<конец файла>" if text == "<EOF>" else text
                    col_end = col_start if lexeme == "<конец файла>" else col_start + len(lexeme) - 1
                    return [
                        _RawError(
                            line=line,
                            column_start=col_start,
                            column_end=col_end,
                            unexpected_lexeme=lexeme,
                            message=f"missing ')' at '{lexeme}'",
                        )
                    ]

                in_lambda_body = False
                in_expr = False
                paren_depth = 0

        return []

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

        inferred = self._infer_missing_rparen_in_lambda_expr(token_stream, parser_listener.errors)

        merged = lexer_listener.errors + parser_listener.errors + inferred
        merged.sort(key=lambda item: (item.line, item.column_start, item.message))
        merged = self._drop_cascade_errors(merged)

        dedup: set[tuple[int, int, str]] = set()
        for err in merged:
            normalized_message = self._normalize_message(err.message, err.unexpected_lexeme)
            key = (err.line, err.column_start, normalized_message)
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
                    message=normalized_message,
                )
            )

        result.recovered_errors = len(result.errors)
        result.success = len(result.errors) == 0
        return result
