import sys

import psycopg2
from PyQt6.QtGui import QStandardItemModel, QAction, QStandardItem
from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtWidgets import (
    QLabel, QMenuBar, QPushButton, QTableView, QToolBar, QMainWindow, QDialog, QMessageBox
)


import sys
import os

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSplitter, QListView, QTextEdit
from PyQt6.QtCore import Qt, QSize, QTimer

from DBConfWindow import DBConfWindow
from DBconfig import DBConfig

# Отключение автоматического масштабирование

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
from airportGrid import AirportGrid




class SegmentedWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Горизонтальный сплиттер
        h_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.departure_panel = AirportGrid(self, "Departure")
        self.arrival_panel = AirportGrid(self, "Arrival")

        h_splitter.addWidget(self.departure_panel)
        h_splitter.addWidget(self.arrival_panel)
        h_splitter.setSizes([900, 900])  # Начальные размеры

        v_loyout = QVBoxLayout()
        v_loyout.addWidget(h_splitter)
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.Searching)
        v_loyout.addWidget(search_button)



        # Вертикальный сплиттер
        v_splitter = QSplitter(Qt.Orientation.Vertical)

        self.routes_grid_model = QStandardItemModel()
        self.routes_grid_model.setHorizontalHeaderLabels(["Air Line", "Plane", "Departure Country", "Departure City", "Departure Airport", "Arrival Country", "Arrival City", "Arrival Airport"])

        route_grid_view = QTableView()
        route_grid_view.verticalHeader().setVisible(False)

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

    def Searching (self):
        if DBConfig.getInstance() is None: return
        dep_country_id ='departure_country_id'
        dep_city_id ='departure_city_id'
        dep_airports = ''
        arr_country_id ='arrival_country_id'
        arr_city_id ='arrival_city_id'
        arr_airports = ''

        dep_data = self.departure_panel.GetSelectedData()
        arr_data = self.arrival_panel.GetSelectedData()
        if dep_data[0] != -1: dep_country_id = dep_data[0]
        if arr_data[0] != -1: arr_country_id = arr_data[0]
        if dep_data[1] != -1: dep_city_id = dep_data[1]
        if arr_data[1] != -1: arr_city_id = arr_data[1]
        if len(dep_data[2]) > 0: dep_airports = f'AND departure_airport_id IN {str(tuple(dep_data[2])).replace(',)',')')} '
        if len(arr_data[2]) > 0: arr_airports = f'AND arrival_airport_id IN {str(tuple(arr_data[2])).replace(',)',')')} '

        query = (
            f'SELECT airline_name, plane_name, departure_country, departure_city, departure_airport, arrival_country, arrival_city, arrival_airport '
            f'FROM public.routes_final '
            f'WHERE '
            f'departure_country_id = {dep_country_id} AND '
            f'departure_city_id = {dep_city_id} AND '
            f'arrival_country_id = {arr_country_id} AND '
            f'arrival_city_id = {arr_city_id} '
            f'{dep_airports}'
            f'{arr_airports}')
        self.routes_grid_model.removeRows(0, self.routes_grid_model.rowCount())
        result = DBConfig.getInstance().GetQueryResult(query)

        for row in result:
            items = []
            for value in row:
                if type(value) is float:
                    f_intem = QStandardItem()
                    f_intem.setData(value, Qt.ItemDataRole.DisplayRole)
                    items.append(f_intem)
                else:
                    items.append(QStandardItem(str(value)))
            self.routes_grid_model.appendRow(items)









class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.segmented_window = SegmentedWindow()
        self.setCentralWidget(self.segmented_window)
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
        QTimer.singleShot(500, self.LoadData)





    def DbConfClicked(self):
        db = DBConfWindow(parent=self)
        db.setModal(True)
        db.show()


    def LoadDb(self):
        try:
            DBConfig.LoadDbFromConfig(self.confpath)
            if DBConfig.getInstance() is None:
                QMessageBox.warning(self, "Warning", "Database not specified. Please configure database first", QMessageBox.StandardButton.Ok)
                self.DbConfClicked()
                return
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Failed connect to database: {str(ex)}", QMessageBox.StandardButton.Ok)





    def LoadData(self):
        self.LoadDb()
        self.segmented_window.departure_panel.LoadContries()
        self.segmented_window.arrival_panel.LoadContries()
        self.segmented_window.departure_panel.LoadCities()
        self.segmented_window.arrival_panel.LoadCities()






if __name__ == "__main__":
    import os

    try:
        print("Текущая рабочая директория:", os.getcwd())
        app = QApplication(sys.argv)
        window = MainApp()

        window.show()
        print(sys.executable)
        sys.exit(app.exec())
    finally:
        DBConfig.getInstance() and DBConfig.getInstance().close()