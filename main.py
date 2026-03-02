"""
Компилятор — кроссплатформенное GUI-приложение для лабораторной работы
«Языковой процессор».

Полноценный интерфейс с:
 - вкладками редактирования и результатов,
 - нумерацией строк, подсветкой синтаксиса,
 - интернационализацией (RU/EN),
 - Drag & Drop, таблицей ошибок, горячими клавишами,
 - масштабированием шрифта и строкой состояния.
"""

import os
import sys

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
    QTextFormat, QIcon,
)
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
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
        "errors_tab": "Ошибки",
        "output_tab": "Вывод",
        "log_tab": "Лог",
        "col_line": "Строка",
        "col_column": "Столбец",
        "col_type": "Тип ошибки",
        "col_description": "Описание",
        "status_line": "Стр: {line}",
        "status_col": "Кол: {col}",
        "status_lines_total": "Строк: {n}",
        "status_modified": "Изменён",
        "status_font_size": "Шрифт: {size}pt",
        "analyzer_stub": (
            "[Пуск] Анализатор (заглушка) — демонстрационные ошибки добавлены."
        ),
        "search_stub": "Поиск…",
        "lang_ru": "Русский",
        "lang_en": "English",
        "toolbar_name": "Основная",
        "font_label": "Шрифт:",
        "about_text": (
            "<h2>Компилятор</h2>"
            "<p>Версия 1.0</p>"
            "<p>Лабораторная работа «Языковой процессор»</p>"
            "<p>Автор: Студент</p>"
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
        "errors_tab": "Errors",
        "output_tab": "Output",
        "log_tab": "Log",
        "col_line": "Line",
        "col_column": "Column",
        "col_type": "Error Type",
        "col_description": "Description",
        "status_line": "Ln: {line}",
        "status_col": "Col: {col}",
        "status_lines_total": "Lines: {n}",
        "status_modified": "Modified",
        "status_font_size": "Font: {size}pt",
        "analyzer_stub": "[Run] Analyzer (stub) — demo errors added.",
        "search_stub": "Find…",
        "lang_ru": "Русский",
        "lang_en": "English",
        "toolbar_name": "Main",
        "font_label": "Font:",
        "about_text": (
            "<h2>Compiler</h2>"
            "<p>Version 1.0</p>"
            "<p>Lab work: Language Processor</p>"
            "<p>Author: Student</p>"
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
    """Возвращает перевод строки по ключу для текущего языка."""
    return TRANSLATIONS.get(_current_lang, TRANSLATIONS["ru"]).get(key, key)






class PascalHighlighter(QSyntaxHighlighter):
    """QSyntaxHighlighter для учебного Pascal-подобного синтаксиса."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self._build_rules()

    def _build_rules(self) -> None:

        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor("#eb6b34"))
        kw_fmt.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "program", "begin", "end", "var", "const", "type",
            "procedure", "function", "if", "then", "else",
            "while", "do", "for", "to", "downto", "repeat", "until",
            "case", "of", "with", "record", "array", "set",
            "and", "or", "not", "div", "mod", "in",
            "int", "real", "boolean", "char", "string",
            "true", "false", "nil", "uses", "unit", "interface",
            "implementation", "write", "writeln", "read", "readln",
            "break", "continue", "exit", "result", "double",
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
    """Виджет-боковик для отображения номеров строк рядом с CodeEditor."""

    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self._editor.line_number_area_paint_event(event)






class CodeEditor(QPlainTextEdit):
    """Текстовый редактор с нумерацией строк и подсветкой синтаксиса."""


    file_dropped = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.highlighter = PascalHighlighter(self.document())

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
        """Устанавливает размер шрифта редактора."""
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
        self._update_line_number_area_width()






class TabData:
    """Хранит состояние одной вкладки редактора."""

    def __init__(
        self, editor: CodeEditor, file_path: str | None = None
    ) -> None:
        self.editor: CodeEditor = editor
        self.file_path: str | None = file_path
        self.is_modified: bool = False






class DoubleClickTabBar(QTabBar):
    """QTabBar, испускающий сигнал при двойном клике по пустой области."""

    double_clicked_empty = pyqtSignal()

    def mouseDoubleClickEvent(self, event) -> None:
        if self.tabAt(event.pos()) == -1:
            self.double_clicked_empty.emit()
        else:
            super().mouseDoubleClickEvent(event)






class HelpDialog(QDialog):
    """Окно справки."""

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
    """Окно «О программе»."""

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






class ResultTabWidget(QTabWidget):
    """Область результатов с тремя фиксированными вкладками."""

    error_double_clicked = pyqtSignal(int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTabsClosable(False)


        self.error_table = QTableWidget(0, 4, self)
        self.error_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.error_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.error_table.horizontalHeader().setStretchLastSection(True)
        self.error_table.verticalHeader().setVisible(False)
        self._update_error_headers()
        self.error_table.cellDoubleClicked.connect(
            self._on_error_double_click
        )


        self.output_text = QPlainTextEdit(self)
        self.output_text.setReadOnly(True)


        self.log_text = QPlainTextEdit(self)
        self.log_text.setReadOnly(True)

        self.addTab(self.error_table, tr("errors_tab"))
        self.addTab(self.output_text, tr("output_tab"))
        self.addTab(self.log_text, tr("log_tab"))



    def retranslate(self) -> None:
        """Обновляет надписи при смене языка."""
        self.setTabText(0, tr("errors_tab"))
        self.setTabText(1, tr("output_tab"))
        self.setTabText(2, tr("log_tab"))
        self._update_error_headers()

    def add_error(
        self, line: int, column: int, error_type: str, description: str
    ) -> None:
        """Добавляет строку ошибки в таблицу."""
        row = self.error_table.rowCount()
        self.error_table.insertRow(row)
        self.error_table.setItem(row, 0, QTableWidgetItem(str(line)))
        self.error_table.setItem(row, 1, QTableWidgetItem(str(column)))
        self.error_table.setItem(row, 2, QTableWidgetItem(error_type))
        self.error_table.setItem(row, 3, QTableWidgetItem(description))

    def clear_errors(self) -> None:
        """Очищает таблицу ошибок."""
        self.error_table.setRowCount(0)

    def set_font_size(self, size: int) -> None:
        """Устанавливает размер шрифта для виджетов результатов."""
        for widget in (self.output_text, self.log_text):
            f = widget.font()
            f.setPointSize(size)
            widget.setFont(f)
        tf = self.error_table.font()
        tf.setPointSize(size)
        self.error_table.setFont(tf)



    def _update_error_headers(self) -> None:
        self.error_table.setHorizontalHeaderLabels([
            tr("col_line"),
            tr("col_column"),
            tr("col_type"),
            tr("col_description"),
        ])
        header = self.error_table.horizontalHeader()
        for i in range(3):
            header.setSectionResizeMode(
                i, QHeaderView.ResizeMode.ResizeToContents
            )
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

    def _on_error_double_click(self, row: int, _col: int) -> None:
        line_item = self.error_table.item(row, 0)
        col_item = self.error_table.item(row, 1)
        if line_item and col_item:
            try:
                self.error_double_clicked.emit(
                    int(line_item.text()), int(col_item.text())
                )
            except ValueError:
                pass






class CompilerWindow(QMainWindow):
    """Главное окно приложения «Компилятор»."""

    DEFAULT_WIDTH = 1100
    DEFAULT_HEIGHT = 700
    DEFAULT_FONT_SIZE = 12
    MIN_FONT_SIZE = 6
    MAX_FONT_SIZE = 72
    _tab_counter = 0





    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self._font_size = self.DEFAULT_FONT_SIZE
        self._tabs_data: dict[int, TabData] = {}

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


        self.action_find = QAction(tr("search_stub"), self)
        self.action_find.setShortcut(QKeySequence("Ctrl+F"))
        self.action_find.triggered.connect(self._on_find_stub)


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


        menu_bar.addAction(self.action_run)


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
        td = self._get_tab_data(index)
        if td and td.is_modified:
            name = self.tab_widget.tabText(index).rstrip(" *")
            reply = QMessageBox.question(
                self,
                tr("save_changes_title"),
                tr("save_changes_msg").format(name=name),
                (
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
                    | QMessageBox.StandardButton.Cancel
                ),
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.tab_widget.setCurrentIndex(index)
                self.on_file_save()
                if td.is_modified:
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
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
        """Вывести сообщение во вкладку «Вывод»."""
        self.result_tabs.output_text.appendPlainText(message)

    def log_debug(self, message: str) -> None:
        """Вывести сообщение во вкладку «Лог»."""
        self.result_tabs.log_text.appendPlainText(message)





    def on_file_new(self) -> None:
        """Создать новую вкладку."""
        self._add_new_tab()
        self.statusBar().showMessage(tr("new_doc"))

    def on_file_open(self) -> None:
        """Открыть файл(ы) в новых вкладках."""
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
        self.log_debug("[Текст] Постановка задачи — не реализовано")

    def on_text_grammar(self) -> None:
        self.log_debug("[Текст] Грамматика — не реализовано")

    def on_text_grammar_class(self) -> None:
        self.log_debug("[Текст] Классификация грамматики — не реализовано")

    def on_text_analysis_method(self) -> None:
        self.log_debug("[Текст] Метод анализа — не реализовано")

    def on_text_test_example(self) -> None:
        self.log_debug("[Текст] Тестовый пример — не реализовано")

    def on_text_references(self) -> None:
        self.log_debug("[Текст] Список литературы — не реализовано")

    def on_text_source_code(self) -> None:
        self.log_debug("[Текст] Исходный код программы — не реализовано")





    def on_run(self) -> None:
        self.result_tabs.clear_errors()
        self.result_tabs.output_text.clear()

        editor = self._current_editor()
        if not editor:
            self.log(tr("analyzer_stub"))
            return

        text = editor.toPlainText()
        self.log(tr("analyzer_stub"))
        self.log(
            f"Текст содержит {editor.blockCount()} строк, "
            f"{len(text)} символов."
        )


        self.result_tabs.add_error(
            1, 1, "Лексическая", "Неопознанный символ '@'"
        )
        self.result_tabs.add_error(
            3, 10, "Синтаксическая", "Ожидался ';' после выражения"
        )
        self.result_tabs.add_error(
            5, 5, "Семантическая", "Переменная 'x' не объявлена"
        )

        self.result_tabs.setCurrentIndex(0)
        self.statusBar().showMessage(tr("analyzer_stub"))

    def _on_error_go_to(self, line: int, col: int) -> None:
        """Переход к строке/столбцу ошибки в редакторе."""
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





    def _on_find_stub(self) -> None:
        self.statusBar().showMessage(tr("search_stub"))





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
            "action_find": "search_stub",
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
            td = self._get_tab_data(i)
            if td and td.is_modified:
                self.tab_widget.setCurrentIndex(i)
                name = self.tab_widget.tabText(i).rstrip(" *")
                reply = QMessageBox.question(
                    self,
                    tr("save_changes_title"),
                    tr("save_changes_msg").format(name=name),
                    (
                        QMessageBox.StandardButton.Yes
                        | QMessageBox.StandardButton.No
                        | QMessageBox.StandardButton.Cancel
                    ),
                    QMessageBox.StandardButton.Yes,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.on_file_save()
                    if td.is_modified:
                        event.ignore()
                        return
                elif reply == QMessageBox.StandardButton.Cancel:
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
