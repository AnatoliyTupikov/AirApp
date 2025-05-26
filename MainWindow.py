import sys

import psycopg2
from PyQt6.QtGui import QStandardItemModel, QAction
from PyQt6.QtWidgets import (
    QLabel, QMenuBar, QPushButton, QTableView, QToolBar, QMainWindow, QDialog, QMessageBox
)


import sys
import os

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSplitter, QListView, QTextEdit
from PyQt6.QtCore import Qt, QSize, QTimer

from DBConfWindow import DBConfWindow
from DBconfig import DBConfig

# Отключаем автоматическое масштабирование

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
from airportGrid import AirportGrid




class SegmentedWindow(QWidget):
    def __init__(self):
        super().__init__()



        # Горизонтальный сплиттер
        h_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Виджеты для левой и правой части
        left_panel = AirportGrid("Departure")
        right_panel = AirportGrid("Arrival")

        h_splitter.addWidget(left_panel)
        h_splitter.addWidget(right_panel)
        h_splitter.setSizes([900, 900])  # Начальные размеры

        v_loyout = QVBoxLayout()
        v_loyout.addWidget(h_splitter)
        v_loyout.addWidget(QPushButton("Search"))



        # Вертикальный сплиттер
        v_splitter = QSplitter(Qt.Orientation.Vertical)

        self.routes_grid_model = QStandardItemModel()
        self.routes_grid_model.setHorizontalHeaderLabels(["123", "sdf", "ed", "cc", "gt", "23"])

        route_grid_view = QTableView()
        route_grid_view.setModel(self.routes_grid_model)

        v_splitter.setLayout(v_loyout)
        v_splitter.addWidget(route_grid_view)
        v_splitter.setSizes([500,100, 700])
        v_splitter.setCollapsible(0, False)
        v_splitter.setCollapsible(1, False)
        v_splitter.setCollapsible(2, False)


        layout = QVBoxLayout()

        layout.addWidget(v_splitter)
        self.setLayout(layout)



class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.confpath = 'config.json'
        self.setWindowTitle("Airplanes route searcher")
        self.setGeometry(100, 100, 2000, 1300)
        self.setMinimumSize(800, 600)
        menubar = self.menuBar()
        dbc_button = QAction("DbConfiguration", self)
        dbc_button.triggered.connect(self.DbConfClicked)
        file_menu = menubar.addMenu("File")
        file_menu.addAction(dbc_button)





    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(500, self.GetDbConfig)


    def DbConfClicked(self):
        db = DBConfWindow(parent=self)
        db.setModal(True)
        db.show()


    def GetDbConfig(self):
        self.db = DBConfig.GetDbConfigFromConfig(self.confpath)
        if self.db is None:
            QMessageBox.warning(self, "Warning", "Database not specified. Please configure database first", QMessageBox.StandardButton.Ok)
            return
        try:
            self.db.CheckDbConnection()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Failed connect to database: {str(ex)}", QMessageBox.StandardButton.Ok)






if __name__ == "__main__":
    import os

    print("Текущая рабочая директория:", os.getcwd())
    app = QApplication(sys.argv)
    window = MainApp()
    window.setCentralWidget(SegmentedWindow())
    window.show()
    sys.exit(app.exec())