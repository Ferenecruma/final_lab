import sys

from sympy.utilities.lambdify import lambdify
from sympy.parsing.sympy_parser import parse_expr

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow,
QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QSpinBox,
QMessageBox, QDesktopWidget)

import backend

#TODO : переделать валидацию мат выражений; добавить в аргументы;
#TODO : сделать ДИЗАЙН =)

def create_hint(string):
        """
        Standart hint for user
        """
        hint = QLabel(string)
        hint.setMaximumHeight(26)
        hint.setFrameStyle(0)
        return hint

def expr_validation(string, a0, a1):
    try:
        expr = lambdify((backend.x0, backend.x1, backend.t), parse_expr(string))
        float(expr(a0, a1, 0))
        return True
    except:
        return False


class MainWindow(QMainWindow):
    default_args = {
                "G": "Piecewise((0, (t - t_) <= 0),(Max(0,((4 * pi * 1 * (t - t_)) ** (-1/2))* exp(-((x0 - x0_) ** 2) / (4 * 1 * (t - t_))),),True))",
                "L": "diff(ex_(t,x0,x1), t) - 1 * (diff(diff(ex_(t,x0,x1), x0), x0) + diff(diff(ex_(t,x0,x1), x1), x1))",
                "y_to_generate_conditions": "10*cos(x0)+10*sin(x1)+t",
        }

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.center_on_screen()
        self.is_added = False

        hint = create_hint("Введіть значення параметрів: ")

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(hint)
        self.main_layout.addWidget(self.create_line_edit_field("G:"))
        self.main_layout.addWidget(self.create_line_edit_field("L:"))
        self.main_layout.addWidget(self.create_line_edit_field("Func to generate cond:"))

        self.buttons_layout = QHBoxLayout()
        self.button_pass_args = QPushButton()
        self.button_pass_args.setText("Ввести")
        self.button_pass_args.clicked.connect(self.input_button_clicked)

        self.button_set_def_args = QPushButton()
        self.button_set_def_args.setText("Заповнити")
        self.button_set_def_args.clicked.connect(self.set_default_values)

        self.buttons_layout.addWidget(self.button_pass_args)
        self.buttons_layout.addWidget(self.button_set_def_args)
        buttons_widget = QWidget()
        buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(buttons_widget)

        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)

        self.setCentralWidget(main_widget)

    def center_on_screen(self):
        # geometry of the main window
        qr = self.frameGeometry()
        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

    def create_field(self, field_title: str, values_num: int=1):
        hint = create_hint(field_title)
        second_input = QHBoxLayout()
        for _ in range(values_num):
            value_input = QSpinBox()
            value_input.setMaximum(500)
            second_input.addWidget(hint)
            second_input.addWidget(value_input)

        second_input_widget = QWidget()
        second_input_widget.setLayout(second_input)

        return second_input_widget

    def create_line_edit_field(self, field_title: str):
        input_layout = QHBoxLayout()
        hint = create_hint(field_title)
        value_input = QLineEdit()

        input_layout.addWidget(hint)
        input_layout.addWidget(value_input)

        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        input_widget

        return input_widget

    def input_button_clicked(self):
        values = self.get_data_from_widgets()
        if not all(val!="" for val in values):
            self.show_popup("Введіть значення параметрів!")
            self.is_added = False
        else:
            args = {k:v for k, v in zip(self.default_args.keys(), values)}
            backend.arg = args
            backend.main()

    def set_default_values(self):
        items = []
        for i in range(1, self.main_layout.count() - 1):
            items.append(self.main_layout.itemAt(i).widget())
        for widget, value in zip(items, self.default_args.values()):
            child_widgets = widget.children()
            if isinstance(child_widgets, list):
                child_widgets[-1].setText(value)

    def get_data_from_widgets(self):
        items, values = [], []
        for i in range(1, self.main_layout.count() - 1):
            items.append(self.main_layout.itemAt(i).widget())
        for widget in items:
            child_widgets = widget.children()
            if isinstance(child_widgets, list):
                values.append(child_widgets[-1].text())
        return values

    def show_popup(self, info: str):
        msg = QMessageBox()
        msg.setWindowTitle("Oops")
        msg.setText(info)
        msg.setIcon(QMessageBox.Warning)

        msg_exec = msg.exec_()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
