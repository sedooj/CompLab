from dataclasses import dataclass


@dataclass(slots=True)
class Lexeme:
    code: int
    token_type: str
    lexeme: str
    line: int
    column_start: int
    column_end: int
    is_error: bool = False
    error_message: str = ""


class LexicalAnalyzer:

    _KEYWORDS = {
        "val": (1, "ключевое слово val"),
        "var": (2, "ключевое слово var"),
        "Int": (3, "тип Int"),
        "String": (19, "тип String"),
        "Double": (20, "тип Double"),
        "Boolean": (21, "тип Boolean"),
        "Float": (22, "тип Float"),
    }

    _SPACE_TOKEN = (23, "разделитель (пробел)")

    _SINGLE_CHAR_TOKENS = {
        ":": (5, "двоеточие"),
        "(": (6, "открывающая скобка"),
        ")": (7, "закрывающая скобка"),
        "/": (8, "оператор деления"),
        "-": (9, "оператор минус"),
        "+": (11, "оператор плюс"),
        "*": (12, "оператор умножения"),
        "=": (13, "оператор присваивания"),
        ";": (14, "конец оператора"),
        "{": (15, "открывающая фигурная скобка"),
        "}": (16, "закрывающая фигурная скобка"),
        ",": (17, "запятая"),
        "%": (18, "оператор остатка"),
        '"': (25, "двойная кавычка"),
    }

    _ARROW_TOKEN = (10, "оператор стрелка")
    _IDENTIFIER_TOKEN = (4, "идентификатор")
    _INTEGER_TOKEN = (24, "целое без знака")

    def analyze(self, text: str) -> list[Lexeme]:
        tokens: list[Lexeme] = []
        i = 0
        line = 1
        col = 1

        while i < len(text):
            ch = text[i]

            if ch == "\n":
                i += 1
                line += 1
                col = 1
                continue

            if ch == "\r":
                i += 1
                continue

            if ch in " \t":
                start_col = col
                while i < len(text) and text[i] in " \t":
                    i += 1
                    col += 1
                tokens.append(
                    Lexeme(
                        code=self._SPACE_TOKEN[0],
                        token_type=self._SPACE_TOKEN[1],
                        lexeme="пробел",
                        line=line,
                        column_start=start_col,
                        column_end=col - 1,
                    )
                )
                continue


            if ch.isalpha():
                start_idx = i
                start_col = col
                while i < len(text) and text[i].isalnum():
                    i += 1
                    col += 1
                lexeme = text[start_idx:i]
                code, token_type = self._KEYWORDS.get(
                    lexeme,
                    self._IDENTIFIER_TOKEN,
                )
                tokens.append(
                    Lexeme(
                        code=code,
                        token_type=token_type,
                        lexeme=lexeme,
                        line=line,
                        column_start=start_col,
                        column_end=col - 1,
                    )
                )
                continue

            if ch.isdigit():
                start_idx = i
                start_col = col
                while i < len(text) and text[i].isdigit():
                    i += 1
                    col += 1
                lexeme = text[start_idx:i]
                tokens.append(
                    Lexeme(
                        code=self._INTEGER_TOKEN[0],
                        token_type=self._INTEGER_TOKEN[1],
                        lexeme=lexeme,
                        line=line,
                        column_start=start_col,
                        column_end=col - 1,
                    )
                )
                continue

            if ch == "-" and i + 1 < len(text) and text[i + 1] == ">":
                tokens.append(
                    Lexeme(
                        code=self._ARROW_TOKEN[0],
                        token_type=self._ARROW_TOKEN[1],
                        lexeme="->",
                        line=line,
                        column_start=col,
                        column_end=col + 1,
                    )
                )
                i += 2
                col += 2
                continue

            single = self._SINGLE_CHAR_TOKENS.get(ch)
            if single is not None:
                tokens.append(
                    Lexeme(
                        code=single[0],
                        token_type=single[1],
                        lexeme=ch,
                        line=line,
                        column_start=col,
                        column_end=col,
                    )
                )
                i += 1
                col += 1
                continue

            bad_symbol = ch
            tokens.append(
                Lexeme(
                    code=-1,
                    token_type="лексическая ошибка",
                    lexeme=bad_symbol,
                    line=line,
                    column_start=col,
                    column_end=col,
                    is_error=True,
                    error_message=f"Недопустимый символ '{bad_symbol}'",
                )
            )
            i += 1
            col += 1

        return tokens
