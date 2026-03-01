import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit,
    QMessageBox, QToolBar, QSplitter,
    QWidget, QVBoxLayout, QStatusBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStyle


class TextProcessorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CompLab1")
        self.resize(1000, 600)

        self.init_ui()

    def init_ui(self):
        # Меняем Horizontal на Vertical
        splitter = QSplitter(Qt.Orientation.Vertical)

        self.editor = QTextEdit()

        self.result = QTextEdit()
        self.result.setReadOnly(True)


        splitter.addWidget(self.editor)
        splitter.addWidget(self.result)

        # Индексы теперь сверху вниз: 0 - верхний блок, 1 - нижний
        splitter.setStretchFactor(0, 2)  # Редактор
        splitter.setStretchFactor(1, 1)  # Результат

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.create_menu()
        self.create_toolbar()
        self.setStatusBar(QStatusBar(self))

    def create_menu(self):
        menubar = self.menuBar()


        file_menu = menubar.addMenu("Файл")
        file_menu.addAction("Создать", self.stub)
        file_menu.addAction("Открыть", self.stub)
        file_menu.addAction("Сохранить", self.stub)
        file_menu.addAction("Сохранить как", self.stub)
        file_menu.addSeparator()
        file_menu.addAction("Выход", self.close)


        edit_menu = menubar.addMenu("Правка")
        edit_menu.addAction("Отменить", self.editor.undo)
        edit_menu.addAction("Повторить", self.editor.redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Вырезать", self.editor.cut)
        edit_menu.addAction("Копировать", self.editor.copy)
        edit_menu.addAction("Вставить", self.editor.paste)
        edit_menu.addAction("Удалить", self.stub)
        edit_menu.addAction("Выделить все", self.editor.selectAll)


        text_menu = menubar.addMenu("Текст")
        items = [
            "Постановка задачи",
            "Грамматика",
            "Классификация грамматики",
            "Метод анализа",
            "Тестовый пример",
            "Список литературы",
            "Исходный код программы"
        ]
        for item in items:
            text_menu.addAction(item, self.stub)


        run_menu = menubar.addMenu("Пуск")
        run_menu.addAction("Запуск анализатора", self.stub)


        help_menu = menubar.addMenu("Справка")
        help_menu.addAction("Вызов справки", self.show_help)
        help_menu.addAction("О программе", self.about)

    def create_toolbar(self):
        toolbar = QToolBar("Панель инструментов")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(toolbar)

        style = self.style()
        actions = [
            ("Создать", style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)),
            ("Открыть", style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)),
            ("Сохранить", style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)),
            ("", None),
            ("Отменить", style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack)),
            ("Повторить", style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward)),
            ("", None),
            ("Вырезать", style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)),
            ("Копировать", style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)),
            ("Вставить", style.standardIcon(QStyle.StandardPixmap.SP_FileDialogListView)),
            ("", None),
            ("Пуск", style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay)),
            ("", None),
            ("Справка", style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)),
            ("О программе", style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)),
        ]

        for name, icon in actions:
            if name == "":
                toolbar.addSeparator()
            else:
                action = QAction(icon, name, self)
                action.triggered.connect(self.stub)
                toolbar.addAction(action)

    def show_help(self):
        QMessageBox.information(
            self,
            "Справка",
            "Реализованы функции меню Файл, Правка и Справка.\n"
            "Меню Текст и команда Пуск будут реализованы позже."
        )

    def about(self):
        QMessageBox.information(
            self,
            "О программе",
            "Текстовый редактор — заготовка языкового процессора\nВерсия 1.0"
        )

    def stub(self):
        print("Z")
        # QMessageBox.information(
        #     self,
        #     "Информация",
        #     "Функция будет реализована позже."
        # )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextProcessorGUI()
    window.show()
    sys.exit(app.exec())