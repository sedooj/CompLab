from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from lexical_analyzer import Lexeme
from syntax_analyzer import SyntaxError, TokenType


NUMERIC_TYPES = {"Int", "Float", "Double"}
INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1


@dataclass(slots=True)
class AstNode:
    line: int
    column: int


@dataclass(slots=True)
class ProgramNode(AstNode):
    declarations: list[ValDeclNode] = field(default_factory=list)


@dataclass(slots=True)
class TypeNode(AstNode):
    name: str


@dataclass(slots=True)
class FunctionTypeNode(AstNode):
    param_types: list[TypeNode] = field(default_factory=list)
    return_type: TypeNode | None = None


@dataclass(slots=True)
class ParamNode(AstNode):
    name: str
    inferred_type: str


@dataclass(slots=True)
class ExprNode(AstNode):
    inferred_type: str


@dataclass(slots=True)
class IdentifierNode(ExprNode):
    name: str


@dataclass(slots=True)
class IntLiteralNode(ExprNode):
    value: int


@dataclass(slots=True)
class BinaryOpNode(ExprNode):
    operator: str
    left: ExprNode
    right: ExprNode


@dataclass(slots=True)
class LambdaNode(AstNode):
    params: list[ParamNode] = field(default_factory=list)
    body: ExprNode | None = None


@dataclass(slots=True)
class ValDeclNode(AstNode):
    name: str
    modifiers: list[str] = field(default_factory=list)
    function_type: FunctionTypeNode | None = None
    value: LambdaNode | None = None


@dataclass(slots=True)
class SemanticResult:
    success: bool = True
    ast: ProgramNode | None = None
    errors: list[SyntaxError] = field(default_factory=list)


@dataclass(slots=True)
class _Symbol:
    name: str
    type_name: str
    line: int
    column: int


@dataclass(slots=True)
class _DeclarationParseResult:
    node: ValDeclNode
    include_in_ast: bool


class _SemanticParseAbort(Exception):
    pass


class _SymbolTable:
    def __init__(self) -> None:
        self._scopes: list[dict[str, _Symbol]] = []

    def push_scope(self) -> None:
        self._scopes.append({})

    def pop_scope(self) -> None:
        if self._scopes:
            self._scopes.pop()

    def lookup_current(self, name: str) -> Optional[_Symbol]:
        if not self._scopes:
            return None
        return self._scopes[-1].get(name)

    def lookup(self, name: str) -> Optional[_Symbol]:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def declare(self, symbol: _Symbol) -> Optional[_Symbol]:
        if not self._scopes:
            self.push_scope()

        existing = self.lookup_current(symbol.name)
        if existing is not None:
            return existing

        self._scopes[-1][symbol.name] = symbol
        return None


class SemanticAnalyzer:
    TYPE_CODES = {
        TokenType.TYPE_INT.value,
        TokenType.TYPE_STRING.value,
        TokenType.TYPE_DOUBLE.value,
        TokenType.TYPE_FLOAT.value,
        TokenType.TYPE_BOOLEAN.value,
    }

    def __init__(self) -> None:
        self._tokens: list[Lexeme] = []
        self._pos = 0
        self._errors: list[SyntaxError] = []
        self._symbols = _SymbolTable()

    def analyze_text(self, text: str, lexer) -> SemanticResult:
        return self.analyze(lexer.analyze(text))

    def analyze(self, lexemes: list[Lexeme]) -> SemanticResult:
        self._tokens = [
            token
            for token in lexemes
            if token.code != TokenType.SPACE.value and not token.is_error
        ]
        self._pos = 0
        self._errors = []
        self._symbols = _SymbolTable()

        program = ProgramNode(line=1, column=1, declarations=[])
        self._symbols.push_scope()

        while self._current() is not None:
            start_pos = self._pos
            try:
                parsed_decl = self._parse_declaration()
            except _SemanticParseAbort:
                break

            if parsed_decl.include_in_ast:
                program.declarations.append(parsed_decl.node)

            if self._pos == start_pos:
                break

        self._symbols.pop_scope()

        if program.declarations:
            program.line = program.declarations[0].line
            program.column = program.declarations[0].column

        return SemanticResult(
            success=len(self._errors) == 0,
            ast=program,
            errors=list(self._errors),
        )

    def _current(self) -> Optional[Lexeme]:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _peek_code(self) -> int:
        token = self._current()
        return token.code if token is not None else -999

    def _advance(self) -> Optional[Lexeme]:
        token = self._current()
        if token is not None:
            self._pos += 1
        return token

    def _expect_code(self, code: int, expected_text: str) -> Lexeme:
        token = self._current()
        if token is None or token.code != code:
            self._add_parse_error(expected_text, token)
            raise _SemanticParseAbort
        self._advance()
        return token

    def _expect_type(self) -> TypeNode:
        token = self._current()
        if token is None or token.code not in self.TYPE_CODES:
            self._add_parse_error("тип (Int, String, Double, Float, Boolean)", token)
            raise _SemanticParseAbort
        self._advance()
        return TypeNode(line=token.line, column=token.column_start, name=token.lexeme)

    def _expect_identifier(self, what: str) -> Lexeme:
        token = self._current()
        if token is None or token.code != TokenType.IDENTIFIER.value:
            self._add_parse_error(what, token)
            raise _SemanticParseAbort
        self._advance()
        return token

    def _add_parse_error(self, expected_text: str, token: Optional[Lexeme]) -> None:
        if token is None:
            self._errors.append(
                SyntaxError(
                    code=-1,
                    error_type="семантическая ошибка",
                    unexpected_lexeme="<конец файла>",
                    expected=expected_text,
                    line=1,
                    column_start=1,
                    column_end=1,
                    message=f"Ожидалось {expected_text}",
                )
            )
            return

        self._errors.append(
            SyntaxError(
                code=-1,
                error_type="семантическая ошибка",
                unexpected_lexeme=token.lexeme,
                expected=expected_text,
                line=token.line,
                column_start=token.column_start,
                column_end=token.column_end,
                message=f"Ожидалось {expected_text}",
            )
        )

    def _add_semantic_error(self, message: str, token: Lexeme) -> None:
        self._errors.append(
            SyntaxError(
                code=-1,
                error_type="семантическая ошибка",
                unexpected_lexeme=token.lexeme,
                expected="",
                line=token.line,
                column_start=token.column_start,
                column_end=token.column_end,
                message=message,
            )
        )

    def _parse_declaration(self) -> _DeclarationParseResult:
        val_token = self._expect_code(TokenType.KEYWORD_VAL.value, "'val'")
        name_token = self._expect_identifier("имя идентификатора")
        self._expect_code(TokenType.COLON.value, "':'")
        declared_type = self._parse_function_type()
        self._expect_code(TokenType.ASSIGN.value, "'='")

        include_in_ast = True
        global_existing = self._symbols.declare(
            _Symbol(
                name=name_token.lexeme,
                type_name="Function",
                line=name_token.line,
                column=name_token.column_start,
            )
        )
        if global_existing is not None:
            include_in_ast = False
            self._add_semantic_error(
                (
                    f"Ошибка: идентификатор \"{name_token.lexeme}\" уже объявлен ранее "
                    f"(строка {global_existing.line})"
                ),
                name_token,
            )

        lambda_node, body_type = self._parse_lambda(declared_type)
        self._expect_code(TokenType.SEMICOLON.value, "';'")

        if declared_type.return_type is not None and body_type != "Unknown":
            expected_type = declared_type.return_type.name
            if not self._types_compatible(expected_type, body_type):
                self._add_semantic_error(
                    (
                        f"Ошибка: тип инициализирующего значения '{body_type}' "
                        f"не совместим с объявленным типом '{expected_type}'"
                    ),
                    val_token,
                )

        node = ValDeclNode(
            line=val_token.line,
            column=val_token.column_start,
            name=name_token.lexeme,
            modifiers=["val"],
            function_type=declared_type,
            value=lambda_node,
        )
        return _DeclarationParseResult(node=node, include_in_ast=include_in_ast)

    def _parse_function_type(self) -> FunctionTypeNode:
        lparen = self._expect_code(TokenType.LPAREN.value, "'('")

        param_types: list[TypeNode] = [self._expect_type()]
        while self._peek_code() == TokenType.COMMA.value:
            self._advance()
            param_types.append(self._expect_type())

        self._expect_code(TokenType.RPAREN.value, "')'")
        self._expect_code(TokenType.ARROW.value, "'->'")
        return_type = self._expect_type()

        return FunctionTypeNode(
            line=lparen.line,
            column=lparen.column_start,
            param_types=param_types,
            return_type=return_type,
        )

    def _parse_lambda(self, function_type: FunctionTypeNode) -> tuple[LambdaNode, str]:
        lbrace = self._expect_code(TokenType.LBRACE.value, "'{'")
        raw_params = self._parse_lambda_params()
        self._expect_code(TokenType.ARROW.value, "'->'")

        lambda_params: list[ParamNode] = []
        self._symbols.push_scope()

        if len(raw_params) != len(function_type.param_types):
            self._add_semantic_error(
                (
                    "Ошибка: количество параметров лямбда-выражения "
                    f"({len(raw_params)}) не совпадает с объявленным типом "
                    f"({len(function_type.param_types)})"
                ),
                lbrace,
            )

        for idx, param_token in enumerate(raw_params):
            inferred_type = (
                function_type.param_types[idx].name
                if idx < len(function_type.param_types)
                else "Unknown"
            )

            lambda_params.append(
                ParamNode(
                    line=param_token.line,
                    column=param_token.column_start,
                    name=param_token.lexeme,
                    inferred_type=inferred_type,
                )
            )

            if param_token.lexeme == "_":
                continue

            existing = self._symbols.declare(
                _Symbol(
                    name=param_token.lexeme,
                    type_name=inferred_type,
                    line=param_token.line,
                    column=param_token.column_start,
                )
            )
            if existing is not None:
                self._add_semantic_error(
                    (
                        f"Ошибка: идентификатор \"{param_token.lexeme}\" уже объявлен ранее "
                        f"(строка {existing.line})"
                    ),
                    param_token,
                )

        body_node = self._parse_expr()
        self._expect_code(TokenType.RBRACE.value, "'}'")
        self._symbols.pop_scope()

        lambda_node = LambdaNode(
            line=lbrace.line,
            column=lbrace.column_start,
            params=lambda_params,
            body=body_node,
        )
        return lambda_node, body_node.inferred_type

    def _parse_lambda_params(self) -> list[Lexeme]:
        params: list[Lexeme] = [self._expect_identifier("имя параметра")]

        while self._peek_code() == TokenType.COMMA.value:
            self._advance()
            params.append(self._expect_identifier("имя параметра"))

        return params

    def _parse_expr(self) -> ExprNode:
        left = self._parse_term()

        while self._peek_code() in {TokenType.PLUS.value, TokenType.MINUS.value}:
            op = self._advance()
            right = self._parse_term()
            assert op is not None
            inferred = self._resolve_binary_type(op, left.inferred_type, right.inferred_type)
            left = BinaryOpNode(
                line=op.line,
                column=op.column_start,
                inferred_type=inferred,
                operator=op.lexeme,
                left=left,
                right=right,
            )

        return left

    def _parse_term(self) -> ExprNode:
        left = self._parse_factor()

        while self._peek_code() in {
            TokenType.MULTIPLY.value,
            TokenType.DIVIDE.value,
            TokenType.MODULO.value,
        }:
            op = self._advance()
            right = self._parse_factor()
            assert op is not None
            inferred = self._resolve_binary_type(op, left.inferred_type, right.inferred_type)
            left = BinaryOpNode(
                line=op.line,
                column=op.column_start,
                inferred_type=inferred,
                operator=op.lexeme,
                left=left,
                right=right,
            )

        return left

    def _parse_factor(self) -> ExprNode:
        token = self._current()
        if token is None:
            self._add_parse_error("выражение", token)
            raise _SemanticParseAbort

        if token.code == TokenType.IDENTIFIER.value:
            self._advance()
            symbol = self._symbols.lookup(token.lexeme)
            if symbol is None or token.lexeme == "_":
                self._add_semantic_error(
                    f"Ошибка: идентификатор \"{token.lexeme}\" используется до объявления",
                    token,
                )
                inferred_type = "Unknown"
            else:
                inferred_type = symbol.type_name

            return IdentifierNode(
                line=token.line,
                column=token.column_start,
                inferred_type=inferred_type,
                name=token.lexeme,
            )

        if token.code == TokenType.NUMBER.value:
            self._advance()
            value = int(token.lexeme)
            if value < INT_MIN or value > INT_MAX:
                self._add_semantic_error(
                    (
                        f"Ошибка: значение {value} выходит за допустимый диапазон "
                        f"для типа Int ({INT_MIN}..{INT_MAX})"
                    ),
                    token,
                )

            return IntLiteralNode(
                line=token.line,
                column=token.column_start,
                inferred_type="Int",
                value=value,
            )

        if token.code == TokenType.LPAREN.value:
            self._advance()
            inner = self._parse_expr()
            self._expect_code(TokenType.RPAREN.value, "')'")
            return inner

        self._add_parse_error("число, идентификатор или '('", token)
        raise _SemanticParseAbort

    def _resolve_binary_type(self, op: Lexeme, left_type: str, right_type: str) -> str:
        if left_type == "Unknown" or right_type == "Unknown":
            return "Unknown"

        if left_type not in NUMERIC_TYPES or right_type not in NUMERIC_TYPES:
            self._add_semantic_error(
                (
                    "Ошибка: арифметический оператор применён к несовместимым типам "
                    f"'{left_type}' и '{right_type}'"
                ),
                op,
            )
            return "Unknown"

        return self._promote_numeric(left_type, right_type)

    @staticmethod
    def _promote_numeric(first: str, second: str) -> str:
        rank = {"Int": 1, "Float": 2, "Double": 3}
        return first if rank[first] >= rank[second] else second

    @staticmethod
    def _types_compatible(expected: str, actual: str) -> bool:
        if expected == actual:
            return True

        if expected == "Double" and actual in {"Float", "Int"}:
            return True

        if expected == "Float" and actual == "Int":
            return True

        return False


def ast_node_name(node: AstNode) -> str:
    if isinstance(node, ProgramNode):
        return "ProgramNode"
    if isinstance(node, ValDeclNode):
        return "ValDeclNode"
    if isinstance(node, FunctionTypeNode):
        return "FunctionTypeNode"
    if isinstance(node, TypeNode):
        return "TypeNode"
    if isinstance(node, LambdaNode):
        return "LambdaNode"
    if isinstance(node, ParamNode):
        return "ParamNode"
    if isinstance(node, BinaryOpNode):
        return "BinaryOpNode"
    if isinstance(node, IdentifierNode):
        return "IdentifierNode"
    if isinstance(node, IntLiteralNode):
        return "IntLiteralNode"
    return node.__class__.__name__


def ast_graph_label(node: AstNode) -> str:
    if isinstance(node, ProgramNode):
        return "ProgramNode"
    if isinstance(node, ValDeclNode):
        modifiers = ", ".join(node.modifiers)
        return f"ValDeclNode\\nname={node.name}\\nmodifiers={modifiers}"
    if isinstance(node, FunctionTypeNode):
        return "FunctionTypeNode"
    if isinstance(node, TypeNode):
        return f"TypeNode\\nname={node.name}"
    if isinstance(node, LambdaNode):
        return "LambdaNode"
    if isinstance(node, ParamNode):
        return f"ParamNode\\nname={node.name}\\ntype={node.inferred_type}"
    if isinstance(node, BinaryOpNode):
        return f"BinaryOpNode\\nop={node.operator}\\ntype={node.inferred_type}"
    if isinstance(node, IdentifierNode):
        return f"IdentifierNode\\nname={node.name}\\ntype={node.inferred_type}"
    if isinstance(node, IntLiteralNode):
        return f"IntLiteralNode\\nvalue={node.value}"
    return ast_node_name(node)


def ast_child_nodes(node: AstNode) -> list[AstNode]:
    if isinstance(node, ProgramNode):
        return list(node.declarations)
    if isinstance(node, ValDeclNode):
        children: list[AstNode] = []
        if node.function_type is not None:
            children.append(node.function_type)
        if node.value is not None:
            children.append(node.value)
        return children
    if isinstance(node, FunctionTypeNode):
        children = list(node.param_types)
        if node.return_type is not None:
            children.append(node.return_type)
        return children
    if isinstance(node, LambdaNode):
        children = list(node.params)
        if node.body is not None:
            children.append(node.body)
        return children
    if isinstance(node, BinaryOpNode):
        return [node.left, node.right]
    return []


def _tree_entries(node: AstNode) -> list[tuple[Optional[str], str | AstNode]]:
    if isinstance(node, ProgramNode):
        return [(None, decl) for decl in node.declarations]

    if isinstance(node, ValDeclNode):
        entries: list[tuple[Optional[str], str | AstNode]] = [
            (None, f'name: "{node.name}"'),
            (None, f"modifiers: {node.modifiers}"),
        ]
        if node.function_type is not None:
            entries.append(("type", node.function_type))
        if node.value is not None:
            entries.append(("value", node.value))
        return entries

    if isinstance(node, FunctionTypeNode):
        entries: list[tuple[Optional[str], str | AstNode]] = []
        if node.param_types:
            entries.append((None, "params"))
            for type_node in node.param_types:
                entries.append((None, type_node))
        if node.return_type is not None:
            entries.append(("returnType", node.return_type))
        return entries

    if isinstance(node, TypeNode):
        return [(None, f'name: "{node.name}"')]

    if isinstance(node, LambdaNode):
        entries: list[tuple[Optional[str], str | AstNode]] = []
        if node.params:
            entries.append((None, "params"))
            for param in node.params:
                entries.append((None, param))
        if node.body is not None:
            entries.append(("body", node.body))
        return entries

    if isinstance(node, ParamNode):
        return [
            (None, f'name: "{node.name}"'),
            (None, f'type: "{node.inferred_type}"'),
        ]

    if isinstance(node, BinaryOpNode):
        return [
            (None, f'operator: "{node.operator}"'),
            (None, f'type: "{node.inferred_type}"'),
            ("left", node.left),
            ("right", node.right),
        ]

    if isinstance(node, IdentifierNode):
        return [
            (None, f'name: "{node.name}"'),
            (None, f'type: "{node.inferred_type}"'),
        ]

    if isinstance(node, IntLiteralNode):
        return [
            (None, f"value: {node.value}"),
            (None, f'type: "{node.inferred_type}"'),
        ]

    return []


def format_ast_tree(root: ProgramNode | None) -> str:
    if root is None:
        return "<AST is empty>"

    lines = [ast_node_name(root)]

    def render_children(node: AstNode, prefix: str) -> None:
        entries = _tree_entries(node)
        for idx, (label, value) in enumerate(entries):
            is_last = idx == len(entries) - 1
            branch = "└──" if is_last else "├──"

            if isinstance(value, str):
                text = f"{label}: {value}" if label else value
                lines.append(f"{prefix}{branch} {text}")
                continue

            head = ast_node_name(value)
            text = f"{label}: {head}" if label else head
            lines.append(f"{prefix}{branch} {text}")
            child_prefix = prefix + ("    " if is_last else "│   ")
            render_children(value, child_prefix)

    render_children(root, "")
    return "\n".join(lines)
