from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from lexical_analyzer import Lexeme


class TokenType(Enum):
    KEYWORD_VAL = 1
    KEYWORD_VAR = 2
    TYPE_INT = 3
    IDENTIFIER = 4
    COLON = 5
    LPAREN = 6
    RPAREN = 7
    DIVIDE = 8
    MINUS = 9
    ARROW = 10
    PLUS = 11
    MULTIPLY = 12
    ASSIGN = 13
    SEMICOLON = 14
    LBRACE = 15
    RBRACE = 16
    COMMA = 17
    MODULO = 18
    TYPE_STRING = 19
    TYPE_DOUBLE = 20
    TYPE_BOOLEAN = 21
    TYPE_FLOAT = 22
    SPACE = 23
    NUMBER = 24
    DOUBLE_QUOTE = 25
    LEXICAL_ERROR = -1


@dataclass
class SyntaxError:
    code: int = -1
    error_type: str = "синтаксическая ошибка"
    unexpected_lexeme: str = ""
    expected: str = ""
    line: int = 1
    column_start: int = 1
    column_end: int = 1
    message: str = ""


@dataclass
class ParseResult:
    success: bool = True
    errors: List[SyntaxError] = field(default_factory=list)
    recovered_errors: int = 0
    tree_nodes: List[str] = field(default_factory=list)


class SyntaxAnalyzer:
    TYPE_CODES = {
        TokenType.TYPE_INT.value,
        TokenType.TYPE_STRING.value,
        TokenType.TYPE_DOUBLE.value,
        TokenType.TYPE_FLOAT.value,
        TokenType.TYPE_BOOLEAN.value,
    }

    EXPR_START_CODES = {
        TokenType.IDENTIFIER.value,
        TokenType.NUMBER.value,
        TokenType.LPAREN.value,
    }

    OPERATOR_CODES = {
        TokenType.PLUS.value,
        TokenType.MINUS.value,
        TokenType.MULTIPLY.value,
        TokenType.DIVIDE.value,
        TokenType.MODULO.value,
    }

    def __init__(self) -> None:
        self.lexemes: List[Lexeme] = []
        self.current_pos: int = 0
        self.errors: List[SyntaxError] = []
        self.result: ParseResult = ParseResult()
        self._seen_error_positions: set[tuple[int, int, str]] = set()

    def analyze(self, lexemes: List[Lexeme]) -> ParseResult:
        self.lexemes = [lex for lex in lexemes if lex.code != TokenType.SPACE.value]
        self.current_pos = 0
        self.errors = []
        self.result = ParseResult(success=True, errors=[], recovered_errors=0)
        self._seen_error_positions = set()

        if not self.lexemes:
            return self.result

        self._parse_start()

        # Report every real trailing token as a separate error.
        while self.current_pos < len(self.lexemes):
            self._error("Неожиданные токены в конце выражения", "конец выражения")
            self._advance()

        self.result.errors = self.errors
        self.result.success = len(self.errors) == 0
        return self.result

    def _current_lexeme(self) -> Optional[Lexeme]:
        if self.current_pos < len(self.lexemes):
            return self.lexemes[self.current_pos]
        return None

    def _peek_code(self) -> int:
        lex = self._current_lexeme()
        return lex.code if lex else -999

    def _peek_next_code(self) -> int:
        idx = self.current_pos + 1
        if idx < len(self.lexemes):
            return self.lexemes[idx].code
        return -999

    def _advance(self) -> Optional[Lexeme]:
        lex = self._current_lexeme()
        if lex is not None:
            self.current_pos += 1
        return lex

    @staticmethod
    def _looks_like_val_typo(text: str) -> bool:
        candidate = (text or "").strip().lower()
        target = "val"

        # Fast path for very common keyboard transposition: vla.
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

    def _synchronize(self, sync_tokens: set[int]) -> None:
        while self.current_pos < len(self.lexemes):
            if self._peek_code() in sync_tokens:
                return
            self._advance()

    def _error(self, message: str, expected: str = "") -> None:
        lex = self._current_lexeme()

        if lex is None:
            if self.lexemes:
                last = self.lexemes[-1]
                line = last.line
                col = last.column_end + 1
            else:
                line = 1
                col = 1
            key = (line, col, "<eof>")
            if key in self._seen_error_positions:
                return
            self._seen_error_positions.add(key)
            self.errors.append(
                SyntaxError(
                    code=-1,
                    error_type="синтаксическая ошибка",
                    unexpected_lexeme="<конец файла>",
                    expected=expected,
                    line=line,
                    column_start=col,
                    column_end=col,
                    message=message,
                )
            )
            self.result.recovered_errors += 1
            return

        key = (lex.line, lex.column_start, message)
        if key in self._seen_error_positions:
            return
        self._seen_error_positions.add(key)
        self.errors.append(
            SyntaxError(
                code=-1,
                error_type="синтаксическая ошибка",
                unexpected_lexeme=lex.lexeme,
                expected=expected,
                line=lex.line,
                column_start=lex.column_start,
                column_end=lex.column_end,
                message=message,
            )
        )
        self.result.recovered_errors += 1

    def _parse_start(self) -> None:
        # <START> -> 'val' <IDENTIFIER> ':' <ARG_LIST> '->' <TYPE> '=' '{' ... '}' ';'
        if self._peek_code() != TokenType.KEYWORD_VAL.value:
            if self._peek_code() == TokenType.IDENTIFIER.value:
                self._error("Ожидалось 'val'", "'val'")
                # If token looks like a typo of 'val' (e.g. "vala"), consume it.
                # Otherwise keep it as function identifier to avoid a false
                # secondary error "Ожидалось имя функции".
                current = self._current_lexeme()
                text = current.lexeme if current is not None else ""
                if self._looks_like_val_typo(text):
                    self._advance()
            else:
                # Count each unexpected leading symbol as a separate real error.
                while (
                    self._current_lexeme() is not None
                    and self._peek_code() != TokenType.KEYWORD_VAL.value
                    and self._peek_code() != TokenType.IDENTIFIER.value
                ):
                    self._error("Ожидалось 'val'", "'val'")
                    self._advance()

                if self._peek_code() == TokenType.KEYWORD_VAL.value:
                    self._advance()
                elif self._peek_code() is None or self._current_lexeme() is None:
                    return
        else:
            self._advance()

        identifier_ok = self._parse_identifier()
        if not identifier_ok:
            # Recover from a bad/missing function name without immediately
            # emitting a cascade ':' error on the same malformed token.
            while (
                self._current_lexeme() is not None
                and self._peek_code() not in {TokenType.COLON.value, TokenType.LPAREN.value}
            ):
                self._advance()

        if self._peek_code() != TokenType.COLON.value:
            self._error("Ожидалось ':'", "':'")
            self._synchronize({TokenType.COLON.value, TokenType.LPAREN.value})
            if self._peek_code() == TokenType.COLON.value:
                self._advance()
        else:
            self._advance()

        self._parse_arg_list()
        self._parse_return_type()
        self._parse_assign()
        body_closed = self._parse_lambda_body()
        if body_closed:
            self._parse_end()

    def _parse_identifier(self) -> bool:
        if self._peek_code() != TokenType.IDENTIFIER.value:
            self._error("Ожидалось имя функции", "идентификатор")
            return False
        self._advance()
        return True

    def _parse_type(self) -> bool:
        if self._peek_code() in self.TYPE_CODES:
            self._advance()
            return True

        self._error("Ожидался тип (Int, String, Double, Float, Boolean)", "тип")
        if self._current_lexeme() is not None:
            self._advance()
        return False

    def _parse_arg_list(self) -> None:
        if self._peek_code() != TokenType.LPAREN.value:
            self._error("Ожидалась '('", "'('")
            self._synchronize({TokenType.LPAREN.value, TokenType.ARROW.value})
            if self._peek_code() == TokenType.LPAREN.value:
                self._advance()
            else:
                return
        else:
            self._advance()

        self._parse_type()

        while self._peek_code() == TokenType.COMMA.value:
            self._advance()
            self._parse_type()

        if self._peek_code() != TokenType.RPAREN.value:
            self._error("Ожидалась ')'", "')'")
            self._synchronize({TokenType.RPAREN.value, TokenType.ARROW.value})
            if self._peek_code() == TokenType.RPAREN.value:
                self._advance()
        else:
            self._advance()

    def _parse_return_type(self) -> None:
        if self._peek_code() != TokenType.ARROW.value:
            self._error("Ожидалась '->'", "'->'")
            # If user wrote '-' instead of '->', consume only '-' and continue.
            if self._peek_code() == TokenType.MINUS.value and self._peek_next_code() != TokenType.ARROW.value:
                self._advance()
            self._synchronize(self.TYPE_CODES | {TokenType.ASSIGN.value})
            if self._peek_code() == TokenType.ASSIGN.value:
                return
        else:
            self._advance()

        if self._peek_code() in self.TYPE_CODES:
            self._advance()
        else:
            self._error("Ожидался тип (Int, String, Double, Float, Boolean)", "тип")
            self._synchronize({TokenType.ASSIGN.value, TokenType.LBRACE.value})

    def _parse_assign(self) -> None:
        if self._current_lexeme() is None:
            self._error("Ожидалось '='", "'='")
            return

        if self._peek_code() != TokenType.ASSIGN.value:
            self._error("Ожидалось '='", "'='")
            self._synchronize({TokenType.ASSIGN.value, TokenType.LBRACE.value})
            if self._peek_code() == TokenType.ASSIGN.value:
                self._advance()
        else:
            self._advance()

    def _parse_lambda_body(self) -> bool:
        if self._current_lexeme() is None:
            self._error("Ожидалась '{'", "'{'")
            return False

        if self._peek_code() != TokenType.LBRACE.value:
            self._error("Ожидалась '{'", "'{'")
            self._synchronize({TokenType.LBRACE.value, TokenType.RBRACE.value, TokenType.SEMICOLON.value})
            if self._peek_code() == TokenType.LBRACE.value:
                self._advance()
            else:
                # Consume closing markers to avoid cascade of trailing token errors
                # after a single missing opening brace.
                if self._peek_code() == TokenType.RBRACE.value:
                    self._advance()
                if self._peek_code() == TokenType.SEMICOLON.value:
                    self._advance()
                return False
        else:
            self._advance()

        self._parse_param_list()

        if self._peek_code() != TokenType.ARROW.value:
            self._error("Ожидалась '->'", "'->'")
            if self._peek_code() == TokenType.MINUS.value and self._peek_next_code() != TokenType.ARROW.value:
                self._advance()
            self._synchronize(self.EXPR_START_CODES | {TokenType.RBRACE.value})
        else:
            self._advance()

        if self._peek_code() == TokenType.RBRACE.value:
            self._error("Ожидалось выражение после '->'", "выражение")
        else:
            self._parse_expr()

        if self._peek_code() != TokenType.RBRACE.value:
            self._error("Ожидалась '}'", "'}'")
            self._synchronize({TokenType.RBRACE.value, TokenType.SEMICOLON.value})
            if self._peek_code() == TokenType.RBRACE.value:
                self._advance()
                return True
            if self._peek_code() == TokenType.SEMICOLON.value:
                self._advance()
            return False
        else:
            self._advance()
            return True

    def _parse_param_list(self) -> None:
        if self._peek_code() != TokenType.IDENTIFIER.value:
            self._error("Ожидалось имя параметра", "идентификатор")
            self._synchronize({TokenType.ARROW.value, TokenType.IDENTIFIER.value})
            if self._peek_code() == TokenType.ARROW.value:
                return

        if self._peek_code() == TokenType.IDENTIFIER.value:
            self._advance()

        while self._peek_code() == TokenType.COMMA.value:
            self._advance()
            if self._peek_code() != TokenType.IDENTIFIER.value:
                self._error("Ожидалось имя параметра", "идентификатор")
                self._synchronize({TokenType.COMMA.value, TokenType.ARROW.value, TokenType.IDENTIFIER.value})
                if self._peek_code() == TokenType.ARROW.value:
                    return
                if self._peek_code() == TokenType.COMMA.value:
                    continue
            if self._peek_code() == TokenType.IDENTIFIER.value:
                self._advance()

        while self._peek_code() == TokenType.IDENTIFIER.value:
            self._error("Ожидалась ',' между параметрами", "','")
            self._advance()

    def _parse_expr(self) -> None:
        self._parse_term()
        while self._peek_code() in {TokenType.PLUS.value, TokenType.MINUS.value}:
            self._advance()
            if self._peek_code() in self.OPERATOR_CODES:
                self._error("Ожидалось выражение после оператора", "выражение")
                while self._peek_code() in self.OPERATOR_CODES:
                    self._advance()
                if self._peek_code() not in self.EXPR_START_CODES:
                    return
            self._parse_term()

    def _parse_term(self) -> None:
        self._parse_factor()
        while self._peek_code() in {TokenType.MULTIPLY.value, TokenType.DIVIDE.value, TokenType.MODULO.value}:
            self._advance()
            if self._peek_code() in self.OPERATOR_CODES:
                self._error("Ожидалось выражение после оператора", "выражение")
                while self._peek_code() in self.OPERATOR_CODES:
                    self._advance()
                if self._peek_code() not in self.EXPR_START_CODES:
                    return
            self._parse_factor()

    def _parse_factor(self) -> None:
        code = self._peek_code()
        if code in {TokenType.IDENTIFIER.value, TokenType.NUMBER.value}:
            self._advance()
            return

        if code == TokenType.LPAREN.value:
            self._advance()
            self._parse_expr()
            if self._peek_code() != TokenType.RPAREN.value:
                self._error("Ожидалась ')'", "')'")
                self._synchronize({TokenType.RPAREN.value, TokenType.RBRACE.value, TokenType.SEMICOLON.value})
                if self._peek_code() == TokenType.RPAREN.value:
                    self._advance()
            else:
                self._advance()
            return

        self._error("Ожидалось число, идентификатор или '('", "выражение")
        # Keep structural closers for outer rules to avoid cascades like
        # missing ')' -> missing '}' on the same malformed tail.
        if code in {TokenType.RPAREN.value, TokenType.RBRACE.value, TokenType.SEMICOLON.value}:
            return
        if self._current_lexeme() is not None:
            self._advance()

    def _parse_end(self) -> None:
        if self._peek_code() != TokenType.SEMICOLON.value:
            self._error("Ожидалась ';' в конце выражения", "';'")
            return
        self._advance()
