from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

from lexical_analyzer import Lexeme, LexicalAnalyzer
from antlr_syntax_analyzer import AntlrSyntaxAnalyzer
from syntax_analyzer import SyntaxAnalyzer, SyntaxError
from semantic_analyzer import (
    BinaryOpNode,
    ExprNode,
    IdentifierNode,
    IntLiteralNode,
    ProgramNode,
    SemanticAnalyzer,
    ValDeclNode,
    format_ast_tree,
)
from regex_search import RegexSearchMode, RegexSearchService, SearchMatch

from PyQt6.QtCore import (
    QMimeData,
    QRect,
    QRegularExpression,
    QSize,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QAction,
    QActionGroup,
    QBrush,
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QKeySequence,
    QPainter,
    QPaintEvent,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
    QIcon,
    QPen,
    QPixmap,
    QWheelEvent,
)
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QStyle,
    QTabBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


TRANSLATIONS = {
    "ru": {
        "window_title": "Компилятор",
        "file": "Файл",
        "edit": "Правка",
        "text": "Текст",
        "run_menu": "Пуск",
        "help_menu": "Справка",
        "language_menu": "Язык",
        "new": "Создать",
        "open": "Открыть",
        "save": "Сохранить",
        "save_as": "Сохранить как…",
        "exit": "Выход",
        "undo": "Отменить",
        "redo": "Повторить",
        "cut": "Вырезать",
        "copy": "Копировать",
        "paste": "Вставить",
        "delete": "Удалить",
        "select_all": "Выделить все",
        "zoom_in": "Увеличить текст",
        "zoom_out": "Уменьшить текст",
        "zoom_reset": "Сбросить масштаб",
        "task": "Постановка задачи",
        "grammar": "Грамматика",
        "grammar_class": "Классификация грамматики",
        "analysis_method": "Метод анализа",
        "test_example": "Тестовый пример",
        "references": "Список литературы",
        "source_code": "Исходный код программы",
        "run": "Пуск",
        "help": "Вызов справки",
        "about": "О программе",
        "about_title": "О программе",
        "help_title": "Справка",
        "ready": "Готово",
        "new_doc": "Новый документ",
        "opened": "Открыт",
        "saved": "Сохранено",
        "error": "Ошибка",
        "save_changes_title": "Сохранить изменения?",
        "save_changes_msg": (
            "В документе «{name}» есть несохранённые изменения.\n"
            "Сохранить их перед продолжением?"
        ),
        "open_file_title": "Открыть файл",
        "save_as_title": "Сохранить как",
        "file_filters": "Текстовые файлы (*.txt);;Все файлы (*.*)",
        "file_open_error": "Не удалось открыть файл:\n{err}",
        "file_save_error": "Не удалось сохранить файл:\n{err}",
        "editor_placeholder": "Введите текст программы…",
        "no_tabs_msg": (
            "Создайте новую вкладку (Ctrl+N)\n"
            "или откройте файл (Ctrl+O)"
        ),
        "untitled": "Безымянный",
        "lexemes_tab": "Лексемы",
        "errors_tab": "Ошибки",
        "output_tab": "Вывод",
        "log_tab": "Лог",
        "col_code": "Условный код",
        "col_lexeme_type": "Тип лексемы",
        "col_lexeme": "Лексема",
        "col_location": "Местоположение",
        "col_error_fragment": "Неверный фрагмент",
        "col_error_location": "Местоположение",
        "col_error_description": "Описание ошибки",
        "errors_count": "Общее количество ошибок:",
        "no_errors": "Нет ошибок",
        "no_errors_found": "Ошибок не найдено",
        "no_code_for_analysis": "Не предоставлен код для анализа",
        "analyzer_mode_menu": "Анализатор",
        "analyzer_mode_label": "Анализатор:",
        "analyzer_mode_recursive": "Рекурсивный спуск",
        "analyzer_mode_antlr": "ANTLR",
        "analyzer_mode_status": "Режим анализатора: {mode}",
        "col_line": "Строка",
        "col_column": "Столбец",
        "col_type": "Тип ошибки",
        "col_description": "Описание",
        "location_format": "строка {line}, {start}-{end}",
        "status_line": "Стр: {line}",
        "status_col": "Кол: {col}",
        "status_lines_total": "Строк: {n}",
        "status_modified": "Изменён",
        "status_font_size": "Шрифт: {size}pt",
        "run_no_active_editor": "Нет активной вкладки для анализа.",
        "run_summary": (
            "Распознано лексем: {tokens}. "
            "Ошибок: {errors}. Строк: {lines}, символов: {chars}."
        ),
        "run_done_ok": "Анализ завершен без ошибок",
        "run_done_with_errors": "Анализ завершен. Ошибок: {errors}",
        "show_ast": "Показать AST",
        "show_ast_no_data": "AST пока недоступно. Выполните анализ корректной строки.",
        "ast_output_header": "AST (текстовое представление):",
        "ast_output_unavailable": "AST не построено из-за ошибок синтаксиса или лексики.",
        "analyzer_stub": (
            "[Пуск] Анализатор (заглушка) — демонстрационные ошибки добавлены."
        ),
        "text_task_stub": "[Текст] Постановка задачи — не реализовано",
        "text_grammar_stub": "[Текст] Грамматика — не реализовано",
        "text_grammar_class_stub": (
            "[Текст] Классификация грамматики — не реализовано"
        ),
        "text_analysis_method_stub": "[Текст] Метод анализа — не реализовано",
        "text_test_example_stub": "[Текст] Тестовый пример — не реализовано",
        "text_references_stub": "[Текст] Список литературы — не реализовано",
        "text_source_code_stub": "[Текст] Исходный код программы — не реализовано",
        "token_type_labels": {
            -1: "лексическая ошибка",
            1: "ключевое слово val",
            2: "ключевое слово var",
            3: "тип Int",
            4: "идентификатор",
            5: "двоеточие",
            6: "открывающая скобка",
            7: "закрывающая скобка",
            8: "оператор деления",
            9: "оператор минус",
            10: "оператор стрелка",
            11: "оператор плюс",
            12: "оператор умножения",
            13: "оператор присваивания",
            14: "конец оператора",
            15: "открывающая фигурная скобка",
            16: "закрывающая фигурная скобка",
            17: "запятая",
            18: "оператор остатка",
            19: "тип String",
            20: "тип Double",
            21: "тип Boolean",
            22: "тип Float",
            23: "разделитель (пробел)",
            24: "целое без знака",
            25: "двойная кавычка",
        },
        "space_lexeme_label": "(пробел)",
        "invalid_symbol_template": "Недопустимый символ '{symbol}'",
        "search_stub": "Поиск…",
        "search_mode_label": "Тип поиска:",
        "search_mode_passport": "Серия и номер российского паспорта",
        "search_mode_amex": "Карта Amex",
        "search_mode_name": "ФИО на английском",
        "search_run": "Поиск",
        "search_results_tab": "Поиск",
        "col_search_match": "Найденная подстрока",
        "col_search_position": "Начальная позиция",
        "col_search_length": "Длина",
        "search_count": "Найдено совпадений: {count}",
        "search_no_matches": "Совпадений не найдено",
        "search_no_data": "Нет данных для поиска",
        "search_done": "Поиск завершен. Совпадений: {count}",
        "search_position_format": "строка {line}, символ {col}",
        "lang_ru": "Русский",
        "lang_en": "English",
        "toolbar_name": "Основная",
        "font_label": "Шрифт:",
        "about_text": (
            "<h2>Компилятор</h2>"
            "<p>Версия 1.0</p>"
            "<p>Лабораторная работа 1. Разработка пользовательского интерфейса (GUI) для языкового процессора</p>"
            "<p>Автор: Герасимов Сергей Павлович</p>"
            "<p>© 2026</p>"
        ),
        "help_text": """\
<h2>Справка — Компилятор</h2>
<h3>Меню «Файл»</h3>
<ul>
  <li><b>Создать</b> (Ctrl+N) — создать новую вкладку.</li>
  <li><b>Открыть</b> (Ctrl+O) — открыть файл в новой вкладке.</li>
  <li><b>Сохранить</b> (Ctrl+S) — сохранить текущую вкладку.</li>
  <li><b>Сохранить как…</b> (Ctrl+Shift+S) — сохранить под новым именем.</li>
  <li><b>Выход</b> (Ctrl+Q) — завершить работу.</li>
</ul>
<h3>Меню «Правка»</h3>
<ul>
  <li><b>Отменить</b> (Ctrl+Z), <b>Повторить</b> (Ctrl+Y)</li>
  <li><b>Вырезать</b>, <b>Копировать</b>, <b>Вставить</b>, <b>Удалить</b></li>
  <li><b>Выделить все</b> (Ctrl+A)</li>
  <li><b>Увеличить/Уменьшить текст</b> (Ctrl+Plus/Minus),
      <b>Сбросить масштаб</b> (Ctrl+0)</li>
</ul>
<h3>Горячие клавиши</h3>
<ul>
  <li>F1 — справка</li>
  <li>F5 / Ctrl+R — запуск анализатора</li>
  <li>Ctrl+N / O / S — файловые операции</li>
  <li>Ctrl++ / Ctrl+- / Ctrl+0 — масштабирование</li>
</ul>
""",
    },
    "en": {
        "window_title": "Compiler",
        "file": "File",
        "edit": "Edit",
        "text": "Text",
        "run_menu": "Run",
        "help_menu": "Help",
        "language_menu": "Language",
        "new": "New",
        "open": "Open",
        "save": "Save",
        "save_as": "Save As…",
        "exit": "Exit",
        "undo": "Undo",
        "redo": "Redo",
        "cut": "Cut",
        "copy": "Copy",
        "paste": "Paste",
        "delete": "Delete",
        "select_all": "Select All",
        "zoom_in": "Zoom In",
        "zoom_out": "Zoom Out",
        "zoom_reset": "Reset Zoom",
        "task": "Problem Statement",
        "grammar": "Grammar",
        "grammar_class": "Grammar Classification",
        "analysis_method": "Analysis Method",
        "test_example": "Test Example",
        "references": "References",
        "source_code": "Source Code",
        "run": "Run",
        "help": "Help Contents",
        "about": "About",
        "about_title": "About",
        "help_title": "Help",
        "ready": "Ready",
        "new_doc": "New document",
        "opened": "Opened",
        "saved": "Saved",
        "error": "Error",
        "save_changes_title": "Save changes?",
        "save_changes_msg": (
            'Document "{name}" has unsaved changes.\n'
            "Save before continuing?"
        ),
        "open_file_title": "Open File",
        "save_as_title": "Save As",
        "file_filters": "Text Files (*.txt);;All Files (*.*)",
        "file_open_error": "Failed to open file:\n{err}",
        "file_save_error": "Failed to save file:\n{err}",
        "editor_placeholder": "Enter program text…",
        "no_tabs_msg": (
            "Create a new tab (Ctrl+N)\n"
            "or open a file (Ctrl+O)"
        ),
        "untitled": "Untitled",
        "lexemes_tab": "Lexemes",
        "errors_tab": "Errors",
        "output_tab": "Output",
        "log_tab": "Log",
        "col_code": "Token Code",
        "col_lexeme_type": "Token Type",
        "col_lexeme": "Lexeme",
        "col_location": "Location",
        "col_error_fragment": "Incorrect Fragment",
        "col_error_location": "Location",
        "col_error_description": "Error Description",
        "errors_count": "Total errors:",
        "no_errors": "No errors",
        "no_errors_found": "No errors found",
        "no_code_for_analysis": "No code provided for analysis",
        "analyzer_mode_menu": "Analyzer",
        "analyzer_mode_label": "Analyzer:",
        "analyzer_mode_recursive": "Recursive Descent",
        "analyzer_mode_antlr": "ANTLR",
        "analyzer_mode_status": "Analyzer mode: {mode}",
        "col_line": "Line",
        "col_column": "Column",
        "col_type": "Error Type",
        "col_description": "Description",
        "location_format": "line {line}, {start}-{end}",
        "status_line": "Ln: {line}",
        "status_col": "Col: {col}",
        "status_lines_total": "Lines: {n}",
        "status_modified": "Modified",
        "status_font_size": "Font: {size}pt",
        "run_no_active_editor": "No active tab to analyze.",
        "run_summary": (
            "Recognized tokens: {tokens}. "
            "Errors: {errors}. Lines: {lines}, chars: {chars}."
        ),
        "run_done_ok": "Analysis completed without errors",
        "run_done_with_errors": "Analysis completed. Errors: {errors}",
        "show_ast": "Show AST",
        "show_ast_no_data": "AST is not available yet. Run analysis for a valid input first.",
        "ast_output_header": "AST (text view):",
        "ast_output_unavailable": "AST was not built because of lexical or syntax errors.",
        "analyzer_stub": "[Run] Analyzer (stub) — demo errors added.",
        "text_task_stub": "[Text] Problem statement — not implemented",
        "text_grammar_stub": "[Text] Grammar — not implemented",
        "text_grammar_class_stub": (
            "[Text] Grammar classification — not implemented"
        ),
        "text_analysis_method_stub": "[Text] Analysis method — not implemented",
        "text_test_example_stub": "[Text] Test example — not implemented",
        "text_references_stub": "[Text] References — not implemented",
        "text_source_code_stub": "[Text] Source code — not implemented",
        "token_type_labels": {
            -1: "lexical error",
            1: "keyword val",
            2: "keyword var",
            3: "type Int",
            4: "identifier",
            5: "colon",
            6: "opening parenthesis",
            7: "closing parenthesis",
            8: "division operator",
            9: "minus operator",
            10: "arrow operator",
            11: "plus operator",
            12: "multiplication operator",
            13: "assignment operator",
            14: "statement terminator",
            15: "opening brace",
            16: "closing brace",
            17: "comma",
            18: "modulo operator",
            19: "type String",
            20: "type Double",
            21: "type Boolean",
            22: "type Float",
            23: "separator (space)",
            24: "unsigned integer",
            25: "double quote",
        },
        "space_lexeme_label": "(space)",
        "invalid_symbol_template": "Invalid symbol '{symbol}'",
        "search_stub": "Find…",
        "search_mode_label": "Search type:",
        "search_mode_passport": "Russian passport series and number",
        "search_mode_amex": "Amex card",
        "search_mode_name": "English full name",
        "search_run": "Search",
        "search_results_tab": "Search",
        "col_search_match": "Matched substring",
        "col_search_position": "Start position",
        "col_search_length": "Length",
        "search_count": "Matches found: {count}",
        "search_no_matches": "No matches found",
        "search_no_data": "No data to search",
        "search_done": "Search finished. Matches: {count}",
        "search_position_format": "line {line}, symbol {col}",
        "lang_ru": "Русский",
        "lang_en": "English",
        "toolbar_name": "Main",
        "font_label": "Font:",
        "about_text": (
            "<h2>Compiler</h2>"
            "<p>Version 1.0</p>"
            "<p>Lab work: Language Processor</p>"
            "<p>Author: Sergei Gerasimov</p>"
            "<p>© 2026</p>"
        ),
        "help_text": """\
<h2>Help — Compiler</h2>
<h3>File Menu</h3>
<ul>
  <li><b>New</b> (Ctrl+N) — create a new tab.</li>
  <li><b>Open</b> (Ctrl+O) — open a file in a new tab.</li>
  <li><b>Save</b> (Ctrl+S) — save the current tab.</li>
  <li><b>Save As…</b> (Ctrl+Shift+S) — save under a new name.</li>
  <li><b>Exit</b> (Ctrl+Q) — quit the application.</li>
</ul>
<h3>Edit Menu</h3>
<ul>
  <li><b>Undo</b> (Ctrl+Z), <b>Redo</b> (Ctrl+Y)</li>
  <li><b>Cut</b>, <b>Copy</b>, <b>Paste</b>, <b>Delete</b></li>
  <li><b>Select All</b> (Ctrl+A)</li>
  <li><b>Zoom In/Out</b> (Ctrl+Plus/Minus),
      <b>Reset Zoom</b> (Ctrl+0)</li>
</ul>
<h3>Shortcuts</h3>
<ul>
  <li>F1 — help</li>
  <li>F5 / Ctrl+R — run analyzer</li>
  <li>Ctrl+N / O / S — file operations</li>
  <li>Ctrl++ / Ctrl+- / Ctrl+0 — zoom</li>
</ul>
""",
    },
}


_current_lang = "ru"


def tr(key: str) -> str:
    return TRANSLATIONS.get(_current_lang, TRANSLATIONS["ru"]).get(key, key)


def tr_value(key: str, default):
    lang_dict = TRANSLATIONS.get(_current_lang, TRANSLATIONS["ru"])
    if key in lang_dict:
        return lang_dict[key]
    return TRANSLATIONS["ru"].get(key, default)


def token_type_label(code: int, is_error: bool) -> str:
    labels = tr_value("token_type_labels", {})
    if not isinstance(labels, dict):
        labels = {}
    if is_error:
        return labels.get(-1, "lexical error")
    return labels.get(code, str(code))


def space_lexeme_label() -> str:
    return tr_value("space_lexeme_label", "(space)")


def invalid_symbol_message(symbol: str) -> str:
    template = tr_value(
        "invalid_symbol_template",
        "Invalid symbol '{symbol}'",
    )
    return template.format(symbol=symbol)


class CodeHighlighter(QSyntaxHighlighter):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self._build_rules()

    def _build_rules(self) -> None:
        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor("#eb6b34"))
        kw_fmt.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "end", "var", "val", "const", "type",
            "fun", "if", "then", "else",
            "while", "do", "for",
            "case", "array", "set",
            "and", "or", "not", "in",
            "Int", "Float", "Boolean", "Char", "String", "Double"
            "true", "false", "null", "interface",
            "implementation", "write", "writeln", "read", "readln",
            "break", "continue", "exit", "result",
            "{", "}", "[", "]", "(", ")"
        ]
        pattern = r"\b(" + "|".join(keywords) + r")\b"
        self._rules.append((
            QRegularExpression(
                pattern,
                QRegularExpression.PatternOption.CaseInsensitiveOption,
            ),
            kw_fmt,
        ))


        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#0080FF"))
        self._rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), num_fmt))


        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#008000"))
        self._rules.append((QRegularExpression(r"'[^']*'"), str_fmt))


        self._rules.append((QRegularExpression(r'"[^"]*"'), str_fmt))


        cmt_fmt = QTextCharFormat()
        cmt_fmt.setForeground(QColor("#808080"))
        cmt_fmt.setFontItalic(True)
        self._rules.append((QRegularExpression(r"//[^\n]*"), cmt_fmt))


        self._rules.append((QRegularExpression(r"\{[^}]*\}"), cmt_fmt))


        self._rules.append((QRegularExpression(r"\(\*.*?\*\)"), cmt_fmt))


        op_fmt = QTextCharFormat()
        op_fmt.setForeground(QColor("#CC7000"))
        self._rules.append((
            QRegularExpression(r":=|<=|>=|<>|[+\-*/=<>]"),
            op_fmt,
        ))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self._editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    file_dropped = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.highlighter = CodeHighlighter(self.document())

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)

        self._update_line_number_area_width(0)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)



    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        space = 6 + self.fontMetrics().horizontalAdvance("9") * digits + 6
        return space

    def _update_line_number_area_width(self, _: int = 0) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(
                cr.left(), cr.top(),
                self.line_number_area_width(), cr.height(),
            )
        )

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#F0F0F0"))
        painter.setPen(QColor("#888888"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(block_number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()



    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path and os.path.isfile(path):
                    self.file_dropped.emit(path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def set_font_size(self, size: int) -> None:
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
        self._update_line_number_area_width()






class TabData:
    def __init__(
        self, editor: CodeEditor, file_path: str | None = None
    ) -> None:
        self.editor: CodeEditor = editor
        self.file_path: str | None = file_path
        self.is_modified: bool = False






class DoubleClickTabBar(QTabBar):
    double_clicked_empty = pyqtSignal()

    def mouseDoubleClickEvent(self, event) -> None:
        if self.tabAt(event.pos()) == -1:
            self.double_clicked_empty.emit()
        else:
            super().mouseDoubleClickEvent(event)






class HelpDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("help_title"))
        self.resize(560, 480)
        layout = QVBoxLayout(self)
        browser = QTextEdit(self)
        browser.setReadOnly(True)
        browser.setHtml(tr("help_text"))
        layout.addWidget(browser)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok, self
        )
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)






class AboutDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("about_title"))
        self.setFixedSize(380, 200)

        layout = QVBoxLayout(self)
        top = QHBoxLayout()

        icon_label = QLabel(self)
        sp = self.style()
        icon_label.setPixmap(
            sp.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
            .pixmap(64, 64)
        )
        top.addWidget(icon_label)

        info = QLabel(tr("about_text"), self)
        info.setTextFormat(Qt.TextFormat.RichText)
        top.addWidget(info, 1)
        layout.addLayout(top)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok, self
        )
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)






class AstGraphicsView(QGraphicsView):
    MIN_SCALE = 0.15
    MAX_SCALE = 8.0
    SCALE_STEP = 1.2

    def __init__(self, scene: QGraphicsScene, parent: QWidget | None = None) -> None:
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setBackgroundBrush(QColor("#e5e7eb"))

    def zoom_by(self, factor: float) -> None:
        current = self.transform().m11()
        if current <= 0:
            self.resetTransform()
            current = 1.0

        target = current * factor
        if target < self.MIN_SCALE:
            factor = self.MIN_SCALE / current
        elif target > self.MAX_SCALE:
            factor = self.MAX_SCALE / current

        self.scale(factor, factor)

    def zoom_in(self) -> None:
        self.zoom_by(self.SCALE_STEP)

    def zoom_out(self) -> None:
        self.zoom_by(1.0 / self.SCALE_STEP)

    def fit_scene(self) -> None:
        bounds = self.sceneRect()
        if bounds.isNull() or bounds.isEmpty():
            return

        self.resetTransform()
        self.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            self.zoom_in()
        elif event.angleDelta().y() < 0:
            self.zoom_out()
        event.accept()


@dataclass(slots=True)
class AstViewNode:
    label: str
    children: list[AstViewNode] = field(default_factory=list)


class AstGraphDialog(QDialog):
    NODE_WIDTH = 220
    NODE_HEIGHT = 76
    H_GAP = 42
    V_GAP = 96

    def __init__(self, root: ProgramNode, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("show_ast"))
        self.resize(1100, 760)
        self._fitted_once = False

        layout = QVBoxLayout(self)
        self.scene = QGraphicsScene(self)
        self.view = AstGraphicsView(self.scene, self)
        self.view.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
        )
        layout.addWidget(self.view)

        self._draw_tree(root)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self._fitted_once:
            self.view.fit_scene()
            self._fitted_once = True

    def keyPressEvent(self, event) -> None:
        if event.matches(QKeySequence.StandardKey.ZoomIn):
            self.view.zoom_in()
            event.accept()
            return

        if event.matches(QKeySequence.StandardKey.ZoomOut):
            self.view.zoom_out()
            event.accept()
            return

        if event.key() == Qt.Key.Key_0:
            self.view.fit_scene()
            event.accept()
            return

        super().keyPressEvent(event)

    def _declaration_label(self, node: ValDeclNode) -> str:
        if node.modifiers:
            return f"{' '.join(node.modifiers).upper()} DECLARATION"
        return "DECLARATION"

    def _build_expr_view(self, expr: ExprNode | None) -> AstViewNode:
        if expr is None:
            return AstViewNode("<EMPTY>")

        if isinstance(expr, BinaryOpNode):
            return AstViewNode(
                f"OPERATOR: {expr.operator}",
                [
                    self._build_expr_view(expr.left),
                    self._build_expr_view(expr.right),
                ],
            )

        if isinstance(expr, IdentifierNode):
            return AstViewNode(expr.name)

        if isinstance(expr, IntLiteralNode):
            return AstViewNode(str(expr.value))

        return AstViewNode(expr.__class__.__name__)

    def _build_decl_view(self, node: ValDeclNode) -> AstViewNode:
        children: list[AstViewNode] = [AstViewNode(f"ID: {node.name}")]

        lambda_children: list[AstViewNode] = []

        if node.value is not None:
            params = [
                AstViewNode(f"{param.name} : {param.inferred_type}")
                for param in node.value.params
            ]
            lambda_children.append(AstViewNode(f"PARAMS ({len(params)})", params))

        if node.function_type is not None:
            arg_children = [
                AstViewNode(type_node.name)
                for type_node in node.function_type.param_types
            ]
            lambda_children.append(AstViewNode(f"ARG TYPES ({len(arg_children)})", arg_children))

            if node.function_type.return_type is not None:
                lambda_children.append(
                    AstViewNode(f"RETURNS: {node.function_type.return_type.name}")
                )

        if node.value is not None:
            lambda_children.append(
                AstViewNode("BODY", [self._build_expr_view(node.value.body)])
            )

        if lambda_children:
            children.append(AstViewNode("LAMBDA FUNCTION", lambda_children))

        return AstViewNode(self._declaration_label(node), children)

    def _build_view_tree(self, root: ProgramNode) -> AstViewNode:
        if len(root.declarations) == 1:
            return self._build_decl_view(root.declarations[0])

        return AstViewNode(
            "PROGRAM",
            [self._build_decl_view(decl) for decl in root.declarations],
        )

    def _layout_tree(
        self,
        node: AstViewNode,
        depth: int,
        left_units: float,
        positions: dict[int, tuple[float, int, AstViewNode]],
        edges: list[tuple[int, int]],
    ) -> float:
        if not node.children:
            positions[id(node)] = (left_units + 0.5, depth, node)
            return 1.0

        cursor = left_units
        total_width = 0.0
        for child in node.children:
            child_width = self._layout_tree(child, depth + 1, cursor, positions, edges)
            cursor += child_width
            total_width += child_width
            edges.append((id(node), id(child)))

        positions[id(node)] = (left_units + total_width / 2.0, depth, node)
        return max(total_width, 1.0)

    def _draw_tree(self, root: ProgramNode) -> None:
        view_root = self._build_view_tree(root)

        positions: dict[int, tuple[float, int, AstViewNode]] = {}
        edges: list[tuple[int, int]] = []
        self._layout_tree(
            view_root,
            depth=0,
            left_units=0.0,
            positions=positions,
            edges=edges,
        )

        x_unit = self.NODE_WIDTH + self.H_GAP
        y_unit = self.NODE_HEIGHT + self.V_GAP

        edge_pen = QPen(QColor("#94a3b8"))
        edge_pen.setWidth(2)

        for parent_id, child_id in edges:
            parent = positions.get(parent_id)
            child = positions.get(child_id)
            if parent is None or child is None:
                continue

            parent_x = parent[0] * x_unit
            parent_y = parent[1] * y_unit
            child_x = child[0] * x_unit
            child_y = child[1] * y_unit

            self.scene.addLine(
                parent_x,
                parent_y + self.NODE_HEIGHT,
                child_x,
                child_y,
                edge_pen,
            )

        node_pen = QPen(QColor("#334155"))
        node_pen.setWidth(2)
        node_brush = QBrush(QColor("#f8fafc"))
        text_font = QFont("Segoe UI", 9)

        for center_x_units, depth, node in positions.values():
            center_x = center_x_units * x_unit
            y = depth * y_unit
            x = center_x - self.NODE_WIDTH / 2

            rect = self.scene.addRect(x, y, self.NODE_WIDTH, self.NODE_HEIGHT, node_pen)
            rect.setBrush(node_brush)

            text = self.scene.addText(node.label, text_font)
            text.setTextWidth(self.NODE_WIDTH - 12)
            text.setDefaultTextColor(QColor("#0f172a"))
            text.setPos(x + 6, y + 6)

        bounds = self.scene.itemsBoundingRect().adjusted(-40, -40, 40, 40)
        self.scene.setSceneRect(bounds)


class ResultTabWidget(QTabWidget):
    error_double_clicked = pyqtSignal(int, int)
    search_double_clicked = pyqtSignal(int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTabsClosable(False)

        self.error_table = QTableWidget(0, 3, self)
        self.error_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.error_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.error_table.horizontalHeader().setStretchLastSection(True)
        self.error_table.verticalHeader().setVisible(False)
        self._update_error_headers()
        self.error_table.cellClicked.connect(
            self._on_error_click
        )

        self.error_count_label = QLabel()
        self.error_count_label.setText(tr("no_errors"))
        self.error_count_label.setStyleSheet("font-weight: bold; padding: 8px;")
        
        error_container = QWidget()
        error_layout = QVBoxLayout(error_container)
        error_layout.setContentsMargins(0, 0, 0, 0)
        error_layout.addWidget(self.error_table)
        error_layout.addWidget(self.error_count_label)
        
        self.output_text = QPlainTextEdit(self)
        self.output_text.setReadOnly(True)

        self.log_text = QPlainTextEdit(self)
        self.log_text.setReadOnly(True)

        self.search_table = QTableWidget(0, 3, self)
        self.search_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.search_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.search_table.verticalHeader().setVisible(False)
        self._update_search_headers()
        self.search_table.cellClicked.connect(self._on_search_click)

        self.search_count_label = QLabel()
        self.search_count_label.setText(tr("search_no_matches"))
        self.search_count_label.setStyleSheet("font-weight: bold; padding: 8px;")

        search_container = QWidget()
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.addWidget(self.search_table)
        search_layout.addWidget(self.search_count_label)

        self.addTab(error_container, tr("errors_tab"))
        self.addTab(self.output_text, tr("output_tab"))
        self.addTab(self.log_text, tr("log_tab"))
        self.addTab(search_container, tr("search_results_tab"))

    def retranslate(self) -> None:
        self.setTabText(0, tr("errors_tab"))
        self.setTabText(1, tr("output_tab"))
        self.setTabText(2, tr("log_tab"))
        self.setTabText(3, tr("search_results_tab"))
        self._update_error_headers()
        self._update_search_headers()

    def add_error(self, fragment: str, line: int, column: int, description: str) -> None:
        """Add an error to the errors table"""
        row = self.error_table.rowCount()
        self.error_table.insertRow(row)

        fragment_item = QTableWidgetItem(fragment)
        fragment_item.setData(Qt.ItemDataRole.UserRole, line)
        fragment_item.setData(Qt.ItemDataRole.UserRole + 1, column)

        location = tr("location_format").format(
            line=line,
            start=column,
            end=column,
        )

        self.error_table.setItem(row, 0, fragment_item)
        self.error_table.setItem(row, 1, QTableWidgetItem(location))
        self.error_table.setItem(row, 2, QTableWidgetItem(description))

    def add_syntax_error(self, error: SyntaxError) -> None:
        """Add a syntax error to the errors table"""
        self.add_error(
            error.unexpected_lexeme,
            error.line,
            error.column_start,
            error.message
        )

    def update_error_count(self, error_count: int) -> None:
        """Update the error count label"""
        if error_count == 0:
            text = tr("no_errors_found")
        else:
            text = f"{tr('errors_count')} {error_count}"
        self.error_count_label.setText(text)

    def set_no_code_message(self) -> None:
        """Show state when editor text is empty"""
        self.error_count_label.setText(tr("no_code_for_analysis"))

    def clear_errors(self) -> None:
        self.error_table.setRowCount(0)
        self.error_count_label.setText(tr("no_errors"))

    def clear_search_results(self) -> None:
        self.search_table.setRowCount(0)
        self.search_count_label.setText(tr("search_no_matches"))

    def set_search_no_data(self) -> None:
        self.search_table.setRowCount(0)
        self.search_count_label.setText(tr("search_no_data"))

    def set_search_results(self, matches: list[SearchMatch]) -> None:
        self.search_table.setRowCount(0)
        if not matches:
            self.search_count_label.setText(tr("search_no_matches"))
            return

        for match in matches:
            row = self.search_table.rowCount()
            self.search_table.insertRow(row)

            value_item = QTableWidgetItem(match.value)
            value_item.setData(Qt.ItemDataRole.UserRole, match.start)
            value_item.setData(Qt.ItemDataRole.UserRole + 1, match.length)
            self.search_table.setItem(row, 0, value_item)

            position_text = tr("search_position_format").format(
                line=match.line,
                col=match.column,
            )
            self.search_table.setItem(row, 1, QTableWidgetItem(position_text))
            self.search_table.setItem(row, 2, QTableWidgetItem(str(match.length)))

        self.search_count_label.setText(
            tr("search_count").format(count=len(matches))
        )

    def set_font_size(self, size: int) -> None:
        for widget in (
            self.output_text,
            self.log_text,
            self.error_table,
            self.search_table,
        ):
            f = widget.font()
            f.setPointSize(size)
            widget.setFont(f)
        lbl_font = self.error_count_label.font()
        lbl_font.setPointSize(size)
        self.error_count_label.setFont(lbl_font)
        self.search_count_label.setFont(lbl_font)

    def _update_error_headers(self) -> None:
        self.error_table.setHorizontalHeaderLabels([
            tr("col_error_fragment"),
            tr("col_error_location"),
            tr("col_error_description"),
        ])
        header = self.error_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def _update_search_headers(self) -> None:
        self.search_table.setHorizontalHeaderLabels([
            tr("col_search_match"),
            tr("col_search_position"),
            tr("col_search_length"),
        ])
        header = self.search_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

    def _on_error_click(self, row: int, _col: int) -> None:
        """Handle click on error table"""
        item = self.error_table.item(row, 0)
        if not item:
            return

        line = item.data(Qt.ItemDataRole.UserRole)
        col = item.data(Qt.ItemDataRole.UserRole + 1)
        if isinstance(line, int) and isinstance(col, int):
            self.error_double_clicked.emit(line, col)

    def _on_search_click(self, row: int, _col: int) -> None:
        item = self.search_table.item(row, 0)
        if not item:
            return

        start = item.data(Qt.ItemDataRole.UserRole)
        length = item.data(Qt.ItemDataRole.UserRole + 1)
        if isinstance(start, int) and isinstance(length, int):
            self.search_double_clicked.emit(start, length)






class CompilerWindow(QMainWindow):
    DEFAULT_WIDTH = 1100
    DEFAULT_HEIGHT = 700
    DEFAULT_FONT_SIZE = 12
    MIN_FONT_SIZE = 6
    MAX_FONT_SIZE = 72
    _tab_counter = 0


    def _format_tr(self, key: str, **kwargs) -> str:
        text = tr(key)
        return text.format(**kwargs) if kwargs else text

    @staticmethod
    def _build_ast_icon() -> QIcon:
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        edge_pen = QPen(QColor("#64748b"))
        edge_pen.setWidth(2)
        painter.setPen(edge_pen)
        painter.drawLine(10, 4, 5, 9)
        painter.drawLine(10, 4, 15, 9)
        painter.drawLine(10, 4, 10, 15)

        node_pen = QPen(QColor("#0f172a"))
        node_pen.setWidth(1)
        painter.setPen(node_pen)
        painter.setBrush(QBrush(QColor("#e2e8f0")))
        for x, y in ((8, 2), (3, 8), (13, 8), (8, 14)):
            painter.drawRoundedRect(x, y, 4, 4, 1.2, 1.2)

        painter.end()
        return QIcon(pixmap)


    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self._font_size = self.DEFAULT_FONT_SIZE
        self._analyzer_mode = "recursive"
        self._tabs_data: dict[int, TabData] = {}
        self.lexical_analyzer = LexicalAnalyzer()
        self.antlr_syntax_analyzer = AntlrSyntaxAnalyzer()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.regex_search_service = RegexSearchService()
        self._has_run_result = False
        self._last_run_no_code = False
        self._last_run_tokens: list[Lexeme] = []
        self._last_run_errors = 0
        self._last_run_syntax_errors: list[SyntaxError] = []
        self._last_run_ast: ProgramNode | None = None
        self._last_run_ast_text = ""
        self._last_run_lines = 0
        self._last_run_chars = 0
        self._output_history: list[tuple[str, str, dict]] = []
        self._log_history: list[tuple[str, str, dict]] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_central_area()
        self._create_status_bar()
        self._update_title()





    def _create_actions(self) -> None:
        sp = self.style()


        self.action_new = QAction(
            sp.standardIcon(QStyle.StandardPixmap.SP_FileIcon),
            tr("new"), self,
        )
        self.action_new.setShortcut(QKeySequence("Ctrl+N"))
        self.action_new.setStatusTip(tr("new"))
        self.action_new.triggered.connect(self.on_file_new)

        self.action_open = QAction(
            sp.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton),
            tr("open"), self,
        )
        self.action_open.setShortcut(QKeySequence("Ctrl+O"))
        self.action_open.setStatusTip(tr("open"))
        self.action_open.triggered.connect(self.on_file_open)

        self.action_save = QAction(
            sp.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton),
            tr("save"), self,
        )
        self.action_save.setShortcut(QKeySequence("Ctrl+S"))
        self.action_save.setStatusTip(tr("save"))
        self.action_save.triggered.connect(self.on_file_save)

        self.action_save_as = QAction(tr("save_as"), self)
        self.action_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.action_save_as.setStatusTip(tr("save_as"))
        self.action_save_as.triggered.connect(self.on_file_save_as)

        self.action_exit = QAction(tr("exit"), self)
        self.action_exit.setShortcut(QKeySequence("Ctrl+Q"))
        self.action_exit.setStatusTip(tr("exit"))
        self.action_exit.triggered.connect(self.close)


        self.action_undo = QAction(
            sp.standardIcon(QStyle.StandardPixmap.SP_ArrowBack),
            tr("undo"), self,
        )
        self.action_undo.setShortcut(QKeySequence("Ctrl+Z"))
        self.action_undo.triggered.connect(self.on_edit_undo)
        self.action_undo.setIcon(QIcon.fromTheme("edit-undo"))

        self.action_redo = QAction(
            sp.standardIcon(QStyle.StandardPixmap.SP_ArrowForward),
            tr("redo"), self,
        )
        self.action_redo.setShortcut(QKeySequence("Ctrl+Y"))
        self.action_redo.triggered.connect(self.on_edit_redo)
        self.action_redo.setIcon(QIcon.fromTheme("edit-redo"))


        self.action_cut = QAction(tr("cut"), self)
        self.action_cut.setShortcut(QKeySequence("Ctrl+X"))
        self.action_cut.triggered.connect(self.on_edit_cut)
        self.action_cut.setIcon(QIcon.fromTheme("edit-cut"))

        self.action_copy = QAction(tr("copy"), self)
        self.action_copy.setShortcut(QKeySequence("Ctrl+C"))
        self.action_copy.triggered.connect(self.on_edit_copy)
        self.action_copy.setIcon(QIcon.fromTheme("edit-copy"))

        self.action_paste = QAction(tr("paste"), self)
        self.action_paste.setShortcut(QKeySequence("Ctrl+V"))
        self.action_paste.triggered.connect(self.on_edit_paste)
        self.action_paste.setIcon(QIcon.fromTheme("edit-paste"))

        self.action_delete = QAction(tr("delete"), self)
        self.action_delete.setShortcut(QKeySequence("Del"))
        self.action_delete.triggered.connect(self.on_edit_delete)

        self.action_select_all = QAction(tr("select_all"), self)
        self.action_select_all.setShortcut(QKeySequence("Ctrl+A"))
        self.action_select_all.triggered.connect(self.on_edit_select_all)


        self.action_zoom_in = QAction(tr("zoom_in"), self)
        self.action_zoom_in.setShortcut(QKeySequence("Ctrl+="))
        self.action_zoom_in.triggered.connect(self.on_zoom_in)

        self.action_zoom_out = QAction(tr("zoom_out"), self)
        self.action_zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        self.action_zoom_out.triggered.connect(self.on_zoom_out)

        self.action_zoom_reset = QAction(tr("zoom_reset"), self)
        self.action_zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        self.action_zoom_reset.triggered.connect(self.on_zoom_reset)


        self.action_task = QAction(tr("task"), self)
        self.action_task.triggered.connect(self.on_text_task)

        self.action_grammar = QAction(tr("grammar"), self)
        self.action_grammar.triggered.connect(self.on_text_grammar)

        self.action_grammar_class = QAction(tr("grammar_class"), self)
        self.action_grammar_class.triggered.connect(self.on_text_grammar_class)

        self.action_analysis_method = QAction(tr("analysis_method"), self)
        self.action_analysis_method.triggered.connect(
            self.on_text_analysis_method
        )

        self.action_test_example = QAction(tr("test_example"), self)
        self.action_test_example.triggered.connect(self.on_text_test_example)

        self.action_references = QAction(tr("references"), self)
        self.action_references.triggered.connect(self.on_text_references)

        self.action_source_code = QAction(tr("source_code"), self)
        self.action_source_code.triggered.connect(self.on_text_source_code)


        self.action_run = QAction(
            sp.standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
            tr("run"), self,
        )
        self.action_run.setShortcuts(
            [QKeySequence("Ctrl+R"), QKeySequence("F5")]
        )
        self.action_run.setStatusTip(tr("run"))
        self.action_run.triggered.connect(self.on_run)
        self.action_run.setIcon(QIcon.fromTheme("media-playback-start"))

        self.action_show_ast = QAction(self._build_ast_icon(), tr("show_ast"), self)
        self.action_show_ast.setShortcut(QKeySequence("Ctrl+Shift+A"))
        self.action_show_ast.setStatusTip(tr("show_ast"))
        self.action_show_ast.triggered.connect(self.on_show_ast)

        self.action_mode_recursive = QAction(
            tr("analyzer_mode_recursive"), self
        )
        self.action_mode_recursive.setCheckable(True)
        self.action_mode_recursive.triggered.connect(
            lambda: self._set_analyzer_mode("recursive")
        )

        self.action_mode_antlr = QAction(tr("analyzer_mode_antlr"), self)
        self.action_mode_antlr.setCheckable(True)
        self.action_mode_antlr.triggered.connect(
            lambda: self._set_analyzer_mode("antlr")
        )

        self.analyzer_mode_group = QActionGroup(self)
        self.analyzer_mode_group.setExclusive(True)
        self.analyzer_mode_group.addAction(self.action_mode_recursive)
        self.analyzer_mode_group.addAction(self.action_mode_antlr)
        self._sync_analyzer_actions()


        self.action_find = QAction(tr("search_run"), self)
        self.action_find.setShortcut(QKeySequence("Ctrl+F"))
        self.action_find.triggered.connect(self.on_regex_search)


        self.action_help = QAction(
            sp.standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton),
            tr("help"), self,
        )
        self.action_help.setShortcut(QKeySequence("F1"))
        self.action_help.triggered.connect(self.on_help)

        self.action_about = QAction(
            sp.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation),
            tr("about"), self,
        )
        self.action_about.triggered.connect(self.on_about)


        self.action_lang_ru = QAction(tr("lang_ru"), self)
        self.action_lang_ru.triggered.connect(
            lambda: self._set_language("ru")
        )

        self.action_lang_en = QAction(tr("lang_en"), self)
        self.action_lang_en.triggered.connect(
            lambda: self._set_language("en")
        )





    def _create_menu(self) -> None:
        menu_bar: QMenuBar = self.menuBar()
        menu_bar.clear()


        self.file_menu = menu_bar.addMenu(tr("file"))
        self.file_menu.addAction(self.action_new)
        self.file_menu.addAction(self.action_open)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_save)
        self.file_menu.addAction(self.action_save_as)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)


        self.edit_menu = menu_bar.addMenu(tr("edit"))
        self.edit_menu.addAction(self.action_undo)
        self.edit_menu.addAction(self.action_redo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_cut)
        self.edit_menu.addAction(self.action_copy)
        self.edit_menu.addAction(self.action_paste)
        self.edit_menu.addAction(self.action_delete)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_select_all)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_zoom_in)
        self.edit_menu.addAction(self.action_zoom_out)
        self.edit_menu.addAction(self.action_zoom_reset)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_find)


        self.text_menu = menu_bar.addMenu(tr("text"))
        self.text_menu.addAction(self.action_task)
        self.text_menu.addAction(self.action_grammar)
        self.text_menu.addAction(self.action_grammar_class)
        self.text_menu.addAction(self.action_analysis_method)
        self.text_menu.addAction(self.action_test_example)
        self.text_menu.addSeparator()
        self.text_menu.addAction(self.action_references)
        self.text_menu.addAction(self.action_source_code)


        self.run_menu = menu_bar.addMenu(tr("run_menu"))
        self.run_menu.addAction(self.action_run)
        self.run_menu.addAction(self.action_show_ast)
        self.run_menu.addSeparator()
        self.analyzer_menu = self.run_menu.addMenu(tr("analyzer_mode_menu"))
        self.analyzer_menu.addAction(self.action_mode_recursive)
        self.analyzer_menu.addAction(self.action_mode_antlr)


        self.lang_menu = menu_bar.addMenu(tr("language_menu"))
        self.lang_menu.addAction(self.action_lang_ru)
        self.lang_menu.addAction(self.action_lang_en)


        self.help_menu = menu_bar.addMenu(tr("help_menu"))
        self.help_menu.addAction(self.action_help)
        self.help_menu.addAction(self.action_about)





    def _create_toolbar(self) -> None:

        for tb in self.findChildren(QToolBar):
            self.removeToolBar(tb)

        toolbar = QToolBar(tr("toolbar_name"), self)
        self.addToolBar(toolbar)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonIconOnly
        )

        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_open)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()
        toolbar.addAction(self.action_undo)
        toolbar.addAction(self.action_redo)
        toolbar.addSeparator()
        toolbar.addAction(self.action_copy)
        toolbar.addAction(self.action_cut)
        toolbar.addAction(self.action_paste)
        toolbar.addSeparator()
        toolbar.addAction(self.action_run)
        toolbar.addAction(self.action_show_ast)
        toolbar.addSeparator()


        self.font_size_spin = QSpinBox(self)
        self.font_size_spin.setRange(self.MIN_FONT_SIZE, self.MAX_FONT_SIZE)
        self.font_size_spin.setValue(self._font_size)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_spin.setToolTip(
            tr("zoom_in") + " / " + tr("zoom_out")
        )
        self.font_size_spin.valueChanged.connect(self._on_font_spin_changed)
        toolbar.addWidget(QLabel(" " + tr("font_label") + " "))
        toolbar.addWidget(self.font_size_spin)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel(" " + tr("analyzer_mode_label") + " "))
        self.analyzer_mode_combo = QComboBox(self)
        self.analyzer_mode_combo.addItem(
            tr("analyzer_mode_recursive"), "recursive"
        )
        self.analyzer_mode_combo.addItem(tr("analyzer_mode_antlr"), "antlr")
        selected_index = (
            1 if self._analyzer_mode == "antlr" else 0
        )
        self.analyzer_mode_combo.setCurrentIndex(selected_index)
        self.analyzer_mode_combo.currentIndexChanged.connect(
            self._on_analyzer_mode_combo_changed
        )
        toolbar.addWidget(self.analyzer_mode_combo)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel(" " + tr("search_mode_label") + " "))
        self.search_mode_combo = QComboBox(self)
        self.search_mode_combo.addItem(
            tr("search_mode_passport"),
            RegexSearchMode.RUSSIAN_PASSPORT,
        )
        self.search_mode_combo.addItem(
            tr("search_mode_amex"),
            RegexSearchMode.AMEX_CARD,
        )
        self.search_mode_combo.addItem(
            tr("search_mode_name"),
            RegexSearchMode.ENGLISH_NAME,
        )
        toolbar.addWidget(self.search_mode_combo)
        toolbar.addAction(self.action_find)

        toolbar.addSeparator()
        toolbar.addAction(self.action_help)
        toolbar.addAction(self.action_about)





    def _create_central_area(self) -> None:

        self.tab_widget = QTabWidget()
        custom_bar = DoubleClickTabBar(self.tab_widget)
        self.tab_widget.setTabBar(custom_bar)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)

        self.tab_widget.tabCloseRequested.connect(
            self._on_tab_close_requested
        )
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        custom_bar.double_clicked_empty.connect(self.on_file_new)


        self.empty_label = QLabel(tr("no_tabs_msg"))
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = self.empty_label.font()
        f.setPointSize(16)
        self.empty_label.setFont(f)
        self.empty_label.setStyleSheet("color: #888;")


        self.editor_stack = QWidget()
        stack_layout = QVBoxLayout(self.editor_stack)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.addWidget(self.tab_widget)
        stack_layout.addWidget(self.empty_label)
        self.tab_widget.hide()
        self.empty_label.show()


        self.result_tabs = ResultTabWidget(self)
        self.result_tabs.error_double_clicked.connect(self._on_error_go_to)
        self.result_tabs.search_double_clicked.connect(self._on_search_go_to)


        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.addWidget(self.editor_stack)
        self.main_splitter.addWidget(self.result_tabs)
        self.main_splitter.setStretchFactor(0, 2)
        self.main_splitter.setStretchFactor(1, 1)
        splitter = self.main_splitter

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(splitter)
        self.setCentralWidget(central)





    def _create_status_bar(self) -> None:
        sb: QStatusBar = self.statusBar()
        sb.showMessage(tr("ready"))

        self.status_line_label = QLabel(tr("status_line").format(line=1))
        self.status_col_label = QLabel(tr("status_col").format(col=1))
        self.status_lines_total_label = QLabel(
            tr("status_lines_total").format(n=0)
        )
        self.status_modified_label = QLabel("")
        self.status_font_label = QLabel(
            tr("status_font_size").format(size=self._font_size)
        )

        for lbl in (
            self.status_line_label,
            self.status_col_label,
            self.status_lines_total_label,
            self.status_modified_label,
            self.status_font_label,
        ):
            sb.addPermanentWidget(lbl)

    def _update_status_bar(self) -> None:
        editor = self._current_editor()
        if editor:
            cur = editor.textCursor()
            line = cur.blockNumber() + 1
            col = cur.columnNumber() + 1
            total = editor.blockCount()
            self.status_line_label.setText(
                tr("status_line").format(line=line)
            )
            self.status_col_label.setText(tr("status_col").format(col=col))
            self.status_lines_total_label.setText(
                tr("status_lines_total").format(n=total)
            )
            td = self._get_tab_data()
            self.status_modified_label.setText(
                tr("status_modified") if td and td.is_modified else ""
            )
        else:
            self.status_line_label.setText(
                tr("status_line").format(line="-")
            )
            self.status_col_label.setText(tr("status_col").format(col="-"))
            self.status_lines_total_label.setText(
                tr("status_lines_total").format(n=0)
            )
            self.status_modified_label.setText("")

        self.status_font_label.setText(
            tr("status_font_size").format(size=self._font_size)
        )


    def _current_editor(self) -> CodeEditor | None:
        w = self.tab_widget.currentWidget()
        return w if isinstance(w, CodeEditor) else None

    def _get_tab_data(self, index: int | None = None) -> TabData | None:
        if index is None:
            index = self.tab_widget.currentIndex()
        if index < 0:
            return None
        w = self.tab_widget.widget(index)
        return self._tabs_data.get(id(w)) if w else None

    def _add_new_tab(
        self,
        title: str | None = None,
        file_path: str | None = None,
        content: str = "",
    ) -> int:
        CompilerWindow._tab_counter += 1

        editor = CodeEditor(self)
        editor.set_font_size(self._font_size)
        editor.setPlaceholderText(tr("editor_placeholder"))

        if content:
            editor.setPlainText(content)

        td = TabData(editor, file_path)
        self._tabs_data[id(editor)] = td

        if title is None:
            title = f"{tr('untitled')} {CompilerWindow._tab_counter}"

        idx = self.tab_widget.addTab(editor, title)
        self.tab_widget.setCurrentIndex(idx)


        editor.textChanged.connect(
            lambda ed=editor: self._on_editor_text_changed(ed)
        )
        editor.cursorPositionChanged.connect(self._update_status_bar)
        editor.file_dropped.connect(self._open_file_in_tab)

        self._update_empty_state()
        return idx

    def _update_empty_state(self) -> None:
        has = self.tab_widget.count() > 0
        self.tab_widget.setVisible(has)
        self.empty_label.setVisible(not has)

    def _on_tab_changed(self, _index: int) -> None:
        self._update_title()
        self._update_status_bar()

    def _on_tab_close_requested(self, index: int) -> None:
        if not self._ask_save_tab_changes(index, allow_cancel=False):
            return

        w = self.tab_widget.widget(index)
        if w:
            self._tabs_data.pop(id(w), None)
        self.tab_widget.removeTab(index)
        self._update_empty_state()
        self._update_title()
        self._update_status_bar()

    def _on_editor_text_changed(self, editor: CodeEditor) -> None:
        td = self._tabs_data.get(id(editor))
        if td and not td.is_modified:
            td.is_modified = True
            idx = self.tab_widget.indexOf(editor)
            if idx >= 0:
                t = self.tab_widget.tabText(idx)
                if not t.endswith(" *"):
                    self.tab_widget.setTabText(idx, t + " *")
            self._update_title()
        self._update_status_bar()

    def _tab_display_name(self, td: TabData) -> str:
        if td.file_path:
            return os.path.basename(td.file_path)
        idx = self.tab_widget.indexOf(td.editor)
        return self.tab_widget.tabText(idx).rstrip(" *")

    def _ask_save_tab_changes(
        self,
        index: int,
        allow_cancel: bool,
    ) -> bool:
        td = self._get_tab_data(index)
        if not td or not td.is_modified:
            return True

        name = self.tab_widget.tabText(index).rstrip(" *")
        buttons = (
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )
        if allow_cancel:
            buttons |= QMessageBox.StandardButton.Cancel

        reply = QMessageBox.question(
            self,
            tr("save_changes_title"),
            tr("save_changes_msg").format(name=name),
            buttons,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.tab_widget.setCurrentIndex(index)
            self.on_file_save()
            return not td.is_modified
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        return True





    def _update_title(self) -> None:
        title = tr("window_title")
        td = self._get_tab_data()
        if td:
            name = self._tab_display_name(td)
            title += f" — {name}"
            if td.is_modified:
                title += " *"
        self.setWindowTitle(title)

    def _on_font_spin_changed(self, value: int) -> None:
        self._font_size = value
        self._apply_font_size()

    def _apply_font_size(self) -> None:
        for td in self._tabs_data.values():
            td.editor.set_font_size(self._font_size)
        self.result_tabs.set_font_size(self._font_size)
        self.font_size_spin.blockSignals(True)
        self.font_size_spin.setValue(self._font_size)
        self.font_size_spin.blockSignals(False)
        self._update_status_bar()

    def log(self, message: str) -> None:
        self._output_history.append(("raw", message, {}))
        self.result_tabs.output_text.appendPlainText(message)

    def log_debug(self, message: str) -> None:
        self._log_history.append(("raw", message, {}))
        self.result_tabs.log_text.appendPlainText(message)

    def log_tr(self, key: str, **kwargs) -> None:
        self._output_history.append(("tr", key, dict(kwargs)))
        self.result_tabs.output_text.appendPlainText(
            self._format_tr(key, **kwargs)
        )

    def log_debug_tr(self, key: str, **kwargs) -> None:
        self._log_history.append(("tr", key, dict(kwargs)))
        self.result_tabs.log_text.appendPlainText(
            self._format_tr(key, **kwargs)
        )

    def _rerender_message_history(self) -> None:
        self.result_tabs.output_text.clear()
        for kind, payload, data in self._output_history:
            if kind == "tr":
                self.result_tabs.output_text.appendPlainText(
                    self._format_tr(payload, **data)
                )
            else:
                self.result_tabs.output_text.appendPlainText(payload)

        self.result_tabs.log_text.clear()
        for kind, payload, data in self._log_history:
            if kind == "tr":
                self.result_tabs.log_text.appendPlainText(
                    self._format_tr(payload, **data)
                )
            else:
                self.result_tabs.log_text.appendPlainText(payload)

    def _render_run_results(
        self,
        update_status: bool = True,
        focus_results: bool = True,
    ) -> None:
        self.result_tabs.clear_errors()
        self.result_tabs.output_text.clear()
        self.result_tabs.log_text.clear()
        self._output_history.clear()
        self._log_history.clear()

        for error in self._last_run_syntax_errors:
            self.result_tabs.add_syntax_error(error)
        
        total_errors = len(self._last_run_syntax_errors)
        if self._last_run_no_code:
            self.result_tabs.set_no_code_message()
        else:
            self.result_tabs.update_error_count(total_errors)

        self.log_tr(
            "run_summary",
            tokens=len(self._last_run_tokens),
            errors=self._last_run_errors,
            lines=self._last_run_lines,
            chars=self._last_run_chars,
        )

        if self._last_run_ast_text:
            self.log("")
            self.log_tr("ast_output_header")
            self.log(self._last_run_ast_text)
        elif not self._last_run_no_code:
            self.log("")
            self.log_tr("ast_output_unavailable")

        if self._last_run_errors:
            completion_key = "run_done_with_errors"
            completion_kwargs = {"errors": self._last_run_errors}
        else:
            completion_key = "run_done_ok"
            completion_kwargs = {}

        self.log_debug_tr(completion_key, **completion_kwargs)
        completion = self._format_tr(completion_key, **completion_kwargs)

        if update_status:
            self.statusBar().showMessage(completion)
        if focus_results:
            self.result_tabs.setCurrentIndex(0)


    def on_file_new(self) -> None:
        self._add_new_tab()
        self.statusBar().showMessage(tr("new_doc"))

    def on_file_open(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, tr("open_file_title"), "", tr("file_filters")
        )
        for p in paths:
            self._open_file_in_tab(p)

    def _open_file_in_tab(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except Exception as exc:
            QMessageBox.critical(
                self, tr("error"), tr("file_open_error").format(err=exc)
            )
            return

        title = os.path.basename(path)
        idx = self._add_new_tab(title=title, file_path=path, content=text)


        td = self._get_tab_data(idx)
        if td:
            td.is_modified = False
            self.tab_widget.setTabText(idx, title)

        self._update_title()
        self.statusBar().showMessage(f"{tr('opened')}: {path}")

    def on_file_save(self) -> None:
        td = self._get_tab_data()
        if not td:
            return
        if td.file_path:
            self._save_tab_to_file(td, td.file_path)
        else:
            self.on_file_save_as()

    def on_file_save_as(self) -> None:
        td = self._get_tab_data()
        if not td:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, tr("save_as_title"), "", tr("file_filters")
        )
        if path:
            self._save_tab_to_file(td, path)

    def _save_tab_to_file(self, td: TabData, path: str) -> None:
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(td.editor.toPlainText())
        except Exception as exc:
            QMessageBox.critical(
                self, tr("error"), tr("file_save_error").format(err=exc)
            )
            return

        td.file_path = path
        td.is_modified = False
        idx = self.tab_widget.indexOf(td.editor)
        if idx >= 0:
            self.tab_widget.setTabText(idx, os.path.basename(path))
        self._update_title()
        self._update_status_bar()
        self.statusBar().showMessage(f"{tr('saved')}: {path}")


    def on_edit_undo(self) -> None:
        e = self._current_editor()
        if e:
            e.undo()

    def on_edit_redo(self) -> None:
        e = self._current_editor()
        if e:
            e.redo()

    def on_edit_cut(self) -> None:
        e = self._current_editor()
        if e:
            e.cut()

    def on_edit_copy(self) -> None:
        e = self._current_editor()
        if e:
            e.copy()

    def on_edit_paste(self) -> None:
        e = self._current_editor()
        if e:
            e.paste()

    def on_edit_delete(self) -> None:
        e = self._current_editor()
        if e:
            c = e.textCursor()
            if c.hasSelection():
                c.removeSelectedText()

    def on_edit_select_all(self) -> None:
        e = self._current_editor()
        if e:
            e.selectAll()





    def on_zoom_in(self) -> None:
        if self._font_size < self.MAX_FONT_SIZE:
            self._font_size += 1
            self._apply_font_size()

    def on_zoom_out(self) -> None:
        if self._font_size > self.MIN_FONT_SIZE:
            self._font_size -= 1
            self._apply_font_size()

    def on_zoom_reset(self) -> None:
        self._font_size = self.DEFAULT_FONT_SIZE
        self._apply_font_size()





    def on_text_task(self) -> None:
        self.log_debug_tr("text_task_stub")

    def on_text_grammar(self) -> None:
        self.log_debug_tr("text_grammar_stub")

    def on_text_grammar_class(self) -> None:
        self.log_debug_tr("text_grammar_class_stub")

    def on_text_analysis_method(self) -> None:
        self.log_debug_tr("text_analysis_method_stub")

    def on_text_test_example(self) -> None:
        self.log_debug_tr("text_test_example_stub")

    def on_text_references(self) -> None:
        self.log_debug_tr("text_references_stub")

    def on_text_source_code(self) -> None:
        self.log_debug_tr("text_source_code_stub")

    def _lexical_error_to_syntax_error(self, token: Lexeme) -> SyntaxError:
        return SyntaxError(
            code=-1,
            error_type="лексическая ошибка",
            unexpected_lexeme=token.lexeme,
            expected="",
            line=token.line,
            column_start=token.column_start,
            column_end=token.column_end,
            message=token.error_message or token_type_label(-1, True),
        )





    def on_run(self) -> None:
        self.result_tabs.clear_errors()
        self.result_tabs.output_text.clear()
        self.result_tabs.log_text.clear()
        self._output_history.clear()
        self._log_history.clear()

        editor = self._current_editor()
        if not editor:
            self._has_run_result = False
            self._last_run_tokens = []
            self._last_run_syntax_errors = []
            self._last_run_ast = None
            self._last_run_ast_text = ""
            self._last_run_errors = 0
            self._last_run_lines = 0
            self._last_run_chars = 0
            self.log_tr("run_no_active_editor")
            return

        text = editor.toPlainText()
        self._last_run_no_code = not text.strip()
        self._last_run_tokens = self.lexical_analyzer.analyze(text)

        lexical_errors: list[SyntaxError] = []
        if self._analyzer_mode == "recursive":
            lexical_errors = [
                self._lexical_error_to_syntax_error(token)
                for token in self._last_run_tokens
                if token.is_error
            ]

        if self._analyzer_mode == "antlr":
            parse_result = self.antlr_syntax_analyzer.analyze_text(text)
        else:
            parse_result = self.syntax_analyzer.analyze(self._last_run_tokens)

        all_errors = lexical_errors + parse_result.errors
        self._last_run_ast = None
        self._last_run_ast_text = ""

        if not all_errors and not self._last_run_no_code:
            semantic_result = self.semantic_analyzer.analyze(self._last_run_tokens)
            self._last_run_ast = semantic_result.ast
            self._last_run_ast_text = format_ast_tree(semantic_result.ast)
            all_errors.extend(semantic_result.errors)

        self._last_run_syntax_errors = all_errors
        self._last_run_errors = len(self._last_run_syntax_errors)
        self._last_run_lines = editor.blockCount()
        self._last_run_chars = len(text)
        self._has_run_result = True

        self._render_run_results(update_status=True, focus_results=True)

    def on_show_ast(self) -> None:
        if self._last_run_ast is None:
            QMessageBox.information(self, tr("show_ast"), tr("show_ast_no_data"))
            return

        AstGraphDialog(self._last_run_ast, self).exec()

    def _on_error_go_to(self, line: int, col: int) -> None:
        editor = self._current_editor()
        if not editor:
            return
        block = editor.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            pos = block.position() + min(col - 1, block.length() - 1)
            cursor = editor.textCursor()
            cursor.setPosition(pos)
            editor.setTextCursor(cursor)
            editor.centerCursor()
            editor.setFocus()

    def _highlight_range(self, start: int, length: int) -> None:
        editor = self._current_editor()
        if not editor:
            return

        cursor = editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(start + length, QTextCursor.MoveMode.KeepAnchor)
        editor.setTextCursor(cursor)
        editor.centerCursor()

        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format.setBackground(QColor("#ffef99"))
        selection.format.setProperty(
            QTextFormat.Property.FullWidthSelection,
            False,
        )
        editor.setExtraSelections([selection])
        editor.setFocus()

    def _clear_highlight(self) -> None:
        editor = self._current_editor()
        if editor:
            editor.setExtraSelections([])

    def _on_search_go_to(self, start: int, length: int) -> None:
        self._highlight_range(start, length)





    def on_regex_search(self) -> None:
        editor = self._current_editor()
        self.result_tabs.clear_search_results()
        self._clear_highlight()

        if not editor:
            self.statusBar().showMessage(tr("run_no_active_editor"))
            self.result_tabs.setCurrentIndex(3)
            return

        text = editor.toPlainText()
        if not text.strip():
            self.result_tabs.set_search_no_data()
            self.result_tabs.setCurrentIndex(3)
            self.statusBar().showMessage(tr("search_no_data"))
            return

        mode_data = self.search_mode_combo.currentData()
        mode = (
            mode_data
            if isinstance(mode_data, RegexSearchMode)
            else RegexSearchMode.AMEX_CARD
        )
        matches = self.regex_search_service.find(text, mode)
        self.result_tabs.set_search_results(matches)
        self.result_tabs.setCurrentIndex(3)
        self.statusBar().showMessage(
            tr("search_done").format(count=len(matches))
        )





    def on_help(self) -> None:
        HelpDialog(self).exec()

    def on_about(self) -> None:
        AboutDialog(self).exec()





    def _set_language(self, lang: str) -> None:
        global _current_lang
        if _current_lang == lang:
            return
        _current_lang = lang
        self._retranslate_ui()

    def _sync_analyzer_actions(self) -> None:
        if self._analyzer_mode == "antlr":
            self.action_mode_antlr.setChecked(True)
        else:
            self.action_mode_recursive.setChecked(True)

    def _set_analyzer_mode(self, mode: str) -> None:
        if mode not in {"recursive", "antlr"}:
            return
        if self._analyzer_mode == mode:
            return
        self._analyzer_mode = mode
        self._sync_analyzer_actions()
        mode_label = tr(
            "analyzer_mode_antlr" if mode == "antlr" else "analyzer_mode_recursive"
        )
        self.statusBar().showMessage(
            tr("analyzer_mode_status").format(mode=mode_label)
        )

    def _on_analyzer_mode_combo_changed(self, index: int) -> None:
        mode = self.analyzer_mode_combo.itemData(index)
        if isinstance(mode, str):
            self._set_analyzer_mode(mode)

    def _retranslate_ui(self) -> None:

        action_keys = {
            "action_new": "new",
            "action_open": "open",
            "action_save": "save",
            "action_save_as": "save_as",
            "action_exit": "exit",
            "action_undo": "undo",
            "action_redo": "redo",
            "action_cut": "cut",
            "action_copy": "copy",
            "action_paste": "paste",
            "action_delete": "delete",
            "action_select_all": "select_all",
            "action_zoom_in": "zoom_in",
            "action_zoom_out": "zoom_out",
            "action_zoom_reset": "zoom_reset",
            "action_task": "task",
            "action_grammar": "grammar",
            "action_grammar_class": "grammar_class",
            "action_analysis_method": "analysis_method",
            "action_test_example": "test_example",
            "action_references": "references",
            "action_source_code": "source_code",
            "action_run": "run",
            "action_show_ast": "show_ast",
            "action_mode_recursive": "analyzer_mode_recursive",
            "action_mode_antlr": "analyzer_mode_antlr",
            "action_find": "search_run",
            "action_help": "help",
            "action_about": "about",
            "action_lang_ru": "lang_ru",
            "action_lang_en": "lang_en",
        }
        for attr, key in action_keys.items():
            action: QAction = getattr(self, attr)
            action.setText(tr(key))
            action.setStatusTip(tr(key))


        self._create_menu()
        self._create_toolbar()


        self.empty_label.setText(tr("no_tabs_msg"))


        self.result_tabs.retranslate()

        if self._has_run_result:
            self._render_run_results(update_status=False, focus_results=False)
        else:
            self._rerender_message_history()


        self._update_title()
        self._update_status_bar()
        self.statusBar().showMessage(tr("ready"))





    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path and os.path.isfile(path):
                    self._open_file_in_tab(path)
            event.acceptProposedAction()





    def showEvent(self, event) -> None:
        super().showEvent(event)

        total = self.main_splitter.height()
        if total > 0:
            self.main_splitter.setSizes([total * 2 // 3, total * 1 // 3])

    def closeEvent(self, event) -> None:
        for i in range(self.tab_widget.count()):
            if not self._ask_save_tab_changes(i, allow_cancel=True):
                event.ignore()
                return
        event.accept()






def main() -> None:
    app = QApplication(sys.argv)


    font = QFont("Consolas", 12)
    font.setStyleHint(QFont.StyleHint.Monospace)
    app.setFont(font)

    window = CompilerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
