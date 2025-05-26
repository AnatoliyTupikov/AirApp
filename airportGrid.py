from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QStandardItemModel
from PyQt6.QtSql import QSqlTableModel
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QCheckBox, QTextEdit, QLabel, QComboBox, \
    QPushButton, QLineEdit, QTableView


class AirportGrid(QWidget):
    def __init__(self, chb_txt):
        super().__init__()
        main_layout = QVBoxLayout()

        # Главный чекбокс
        self.main_chbox = QCheckBox(f"{chb_txt}")
        self.main_chbox.setChecked(False)
        self.main_chbox.stateChanged.connect(self.toggle_controls)

        # Обёртка-контейнер для отключаемой части
        self.control_container = QWidget()
        control_layout = QVBoxLayout()
        self.control_container.setLayout(control_layout)

        # Сетка фильтра
        filter_grid = QGridLayout()

        controls_grid = QGridLayout()

        self.coord_chbox = QCheckBox("Coordinates")
        self.coord_chbox.setChecked(False)
        self.coord_chbox.stateChanged.connect(self.coord_controls)

        controls_grid.addWidget(self.coord_chbox, 0, 0)

        self.double_field = QLineEdit()
        self.double_field2 = QLineEdit()
        self.double_field.setValidator(QDoubleValidator())
        self.double_field2.setValidator(QDoubleValidator())
        self.double_field.setEnabled(self.coord_chbox.isChecked())
        self.double_field2.setEnabled(self.coord_chbox.isChecked())

        controls_grid.addWidget(self.double_field, 0, 1)
        controls_grid.addWidget(QLabel("—"), 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        controls_grid.addWidget(self.double_field2, 0, 3)

        self.country_chbox = QCheckBox("Country")
        self.country_chbox.setChecked(True)
        self.country_chbox.stateChanged.connect(self.country_controls)

        self.country_cbox = QComboBox()
        self.country_cbox.setEditable(True)
        self.country_cbox.setEnabled(self.country_chbox.isChecked())
        self.city_cbox = QComboBox()
        self.city_cbox.setEditable(True)
        self.city_cbox.setEnabled(self.country_chbox.isChecked())


        controls_grid.addWidget(self.country_chbox, 1, 0)
        controls_grid.addWidget(self.country_cbox, 1, 1)
        controls_grid.addWidget(QLabel("City"), 1, 2)
        controls_grid.addWidget(self.city_cbox, 1, 3)

        controls_grid.setColumnStretch(1, 1)
        controls_grid.setColumnStretch(3, 1)

        controls_grid_widget = QWidget()
        controls_grid_widget.setLayout(controls_grid)

        ref_button = QPushButton("Refresh")

        filter_grid.addWidget(controls_grid_widget, 0, 1)
        filter_grid.addWidget(ref_button, 0, 2)

        filter_widget = QWidget()
        filter_widget.setLayout(filter_grid)

        control_layout.addWidget(filter_widget)

        self.airport_grid_model = QStandardItemModel()
        self.airport_grid_model.setHorizontalHeaderLabels(["123", "sdf", "ed", "cc", "gt", "23"])

        airport_grid_view = QTableView()
        airport_grid_view.setModel(self.airport_grid_model)
        control_layout.addWidget(airport_grid_view)

        # Собираем всё вместе
        main_layout.addWidget(self.main_chbox)
        main_layout.addWidget(self.control_container)
        self.setLayout(main_layout)

        # Изначально всё внутри выключено
        self.control_container.setEnabled(False)


    def toggle_controls(self):
        self.control_container.setEnabled(self.main_chbox.isChecked())

    def coord_controls(self):
        self.double_field.setEnabled(self.coord_chbox.isChecked())
        self.double_field2.setEnabled(self.coord_chbox.isChecked())

    def country_controls(self):
        self.country_cbox.setEnabled(self.country_chbox.isChecked())
        self.city_cbox.setEnabled(self.country_chbox.isChecked())








