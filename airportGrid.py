from PyQt6.QtCore import Qt, QLocale, QTimer, QEvent
from PyQt6.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem
from PyQt6.QtSql import QSqlTableModel
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QCheckBox, QTextEdit, QLabel, QComboBox, \
    QPushButton, QLineEdit, QTableView, QHeaderView, QAbstractItemView, QSizePolicy, QMessageBox

from DBconfig import DBConfig
import ValidationClass


class AirportGrid(QWidget):
    def __init__(self, parent, chb_txt):
        super().__init__()
        self.setParent(parent)

        self.main_chbox = QCheckBox(f"{chb_txt}")
        self.main_chbox.setChecked(True)
        self.main_chbox.stateChanged.connect(self.main_enabling)



        self.country_cbox = QComboBox()
        self.country_cbox.setCurrentIndex(0)
        self.country_cbox.currentIndexChanged.connect(self.country_selected)
        self.country_cbox.currentIndexChanged.connect(self.punkt_validate)
        self.country_cbox.setEditable(True)
        self.country_cbox.setMinimumWidth(300)
        self.country_cbox.lineEdit().editingFinished.connect(self.set_text)




        self.city_cbox = QComboBox()
        self.city_cbox.setCurrentIndex(0)
        self.city_cbox.currentIndexChanged.connect(self.city_selected)
        self.city_cbox.currentIndexChanged.connect(self.punkt_validate)
        self.city_cbox.setMinimumWidth(300)
        self.city_cbox.setEditable(True)
        self.city_cbox.lineEdit().editingFinished.connect(self.set_text)



        self.country_layout = QHBoxLayout()
        self.country_layout.addWidget(QLabel("Country:"))
        self.country_layout.addWidget(self.country_cbox)
        self.country_layout.addWidget(QLabel("City:"))
        self.country_layout.addWidget(self.city_cbox)
        self.country_layout.setContentsMargins(25, 0, 0, 0)
        self.country_widget = QWidget()
        self.country_widget.setLayout(self.country_layout)
        self.selected_country_id = -1



        self.airports_toggle = QCheckBox("Airport selection")
        self.airports_toggle.setChecked(False)
        self.airports_toggle.stateChanged.connect(self.airport_selection_enabling)
        self.airports_toggle_layout = QHBoxLayout()
        self.airports_toggle_layout.addWidget(self.airports_toggle)
        self.airports_toggle_layout.setContentsMargins(25, 20, 0, 10)
        self.airports_toggle_widget = QWidget()
        self.airports_toggle_widget.setLayout(self.airports_toggle_layout)

        validator = QDoubleValidator()
        validator.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        validator.setRange(-2147483647, 2147483647, 10)
        self.input_timer = QTimer()
        self.input_timer.setSingleShot(True)
        self.input_timer.timeout.connect(
            lambda:(
                self.coord_validate(self.coord_lat_min, self.coord_lat_max),
                self.coord_validate(self.coord_long_min, self.coord_long_max)
            ))

        min_value_placeholder = 'Min coordinate: No limit...'
        max_value_placeholder = 'Max coordinate: No limit...'

        self.lat_chb = QCheckBox("Latitude:   ")
        self.lat_chb.stateChanged.connect(self.coord_filter_enabling)
        self.coord_lat_min = QLineEdit()
        self.coord_lat_max = QLineEdit()
        self.coord_lat_min.installEventFilter(self)
        self.coord_lat_min.textEdited.connect(self.coord_validate_input_lag)
        self.coord_lat_min.textEdited.connect(self.comma_dot)
        self.coord_lat_max.installEventFilter(self)
        self.coord_lat_max.textEdited.connect(self.coord_validate_input_lag)
        self.coord_lat_max.textEdited.connect(self.comma_dot)
        self.coord_lat_min.setValidator(validator)
        self.coord_lat_min.setPlaceholderText(min_value_placeholder)
        self.coord_lat_max.setValidator(validator)
        self.coord_lat_max.setPlaceholderText(max_value_placeholder)
        self.coord_lat_min.setEnabled(self.airports_toggle.isChecked())
        self.coord_lat_max.setEnabled(self.airports_toggle.isChecked())
        lat_layout = QHBoxLayout()
        lat_layout.addWidget(self.lat_chb)
        lat_layout.addWidget(self.coord_lat_min)
        lat_layout.addWidget(QLabel("—"), alignment=Qt.AlignmentFlag.AlignCenter)
        lat_layout.addWidget(self.coord_lat_max)

        self.long_chb = QCheckBox("Longitude:")
        self.long_chb.stateChanged.connect(self.coord_filter_enabling)
        self.coord_long_min = QLineEdit()
        self.coord_long_max = QLineEdit()
        self.coord_long_min.textEdited.connect(self.coord_validate_input_lag)
        self.coord_long_min.textEdited.connect(self.comma_dot)
        self.coord_long_min.installEventFilter(self)
        self.coord_long_max.textEdited.connect(self.coord_validate_input_lag)
        self.coord_long_max.textEdited.connect(self.comma_dot)
        self.coord_long_max.installEventFilter(self)
        self.coord_long_min.setValidator(validator)
        self.coord_long_min.setPlaceholderText(min_value_placeholder)
        self.coord_long_max.setValidator(validator)
        self.coord_long_max.setPlaceholderText(max_value_placeholder)
        self.coord_long_min.setEnabled(self.airports_toggle.isChecked())
        self.coord_long_max.setEnabled(self.airports_toggle.isChecked())
        long_layout = QHBoxLayout()
        long_layout.addWidget(self.long_chb)
        long_layout.addWidget(self.coord_long_min)
        long_layout.addWidget(QLabel("—"), alignment=Qt.AlignmentFlag.AlignCenter)
        long_layout.addWidget(self.coord_long_max)



        coord_fields_layout = QVBoxLayout()
        coord_fields_layout.addLayout(lat_layout)
        coord_fields_layout.addLayout(long_layout)

        self.coord_filter_button = QPushButton("Set \ncoordinates filter")
        self.coord_filter_button.setEnabled(self.lat_chb.isChecked() or self.long_chb.isChecked())
        self.coord_filter_button.clicked.connect(self.airport_selection_enabling)

        coord_filter_layout = QHBoxLayout()
        coord_filter_layout.addLayout(coord_fields_layout)
        coord_filter_layout.addWidget(self.coord_filter_button)
        coord_filter_layout.setContentsMargins(50, 0, 50, 0)

        self.selected_airports = set()

        self.selected = 0
        self.all_items = 0

        self.airport_grid_model = QStandardItemModel()
        self.headers = [f"✓\n{self.selected} of {self.all_items}", "id", "Name", "City", "Country", "Code", "Latitude",
                        "Longitude"]
        self.airport_grid_model.setHorizontalHeaderLabels(self.headers)
        self.airport_grid_model.itemChanged.connect(self.checkboxInGrid)
        self.airport_grid_view = QTableView()
        self.airport_grid_view.setModel(self.airport_grid_model)
        self.airport_grid_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.airport_grid_view.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.airport_grid_view.setSortingEnabled(True)
        self.airport_grid_view.hideColumn(1)
        self.airport_grid_view.verticalHeader().setVisible(False)
        airport_layout = QVBoxLayout()
        airport_layout.addWidget(self.airport_grid_view)
        airport_layout.setContentsMargins(0, 5, 0, 0)


        airports_selection_layout = QVBoxLayout()
        airports_selection_layout.addLayout(coord_filter_layout)
        airports_selection_layout.addLayout(airport_layout)
        self.airports_selection_widget = QWidget()
        self.airports_selection_widget.setLayout(airports_selection_layout)



        body_layout = QVBoxLayout()
        body_layout.addWidget(self.country_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        body_layout.addWidget(self.airports_toggle_widget)
        body_layout.addWidget(self.airports_selection_widget)


        main_layout = QVBoxLayout()
        main_layout.addWidget(self.main_chbox)
        main_layout.addLayout(body_layout)
        self.main_enabling()

        self.setLayout(main_layout)
        self.airport_selection_enabling()


#==============================================================End of class======================================================================================

    def main_enabling(self):
        self.country_widget.setEnabled(self.main_chbox.isChecked())
        self.airports_toggle_widget.setEnabled(self.main_chbox.isChecked())
        self.airports_selection_widget.setEnabled(self.main_chbox.isChecked())
        self.selected_airports.clear()
        if self.city_cbox.currentData() is not None: self.selected_city_id = self.city_cbox.currentData()[0]
        if self.country_cbox.currentData() is not None: self.selected_city_id = self.country_cbox.currentData()[0]
        if not self.main_chbox.isChecked():
            self.selected_city_id = -1
            self.selected_country_id = -1
        if not self.airports_toggle.isChecked(): self.airport_selection_enabling()

    def country_selected (self):
        self.LoadCities()
        if self.country_cbox.currentData() is not None: self.selected_country_id = self.country_cbox.currentData()[0]
        self.airport_selection_enabling()

    def city_selected (self):
        if self.city_cbox.currentData() is not None: self.selected_city_id = self.city_cbox.currentData()[0]
        self.airport_selection_enabling()


    def airport_selection_enabling(self):
        sender = self.airports_toggle
        self.airports_selection_widget.setEnabled(sender.isChecked())
        self.selected_airports.clear()

        if sender.isChecked():
            self.get_airports_with_filters()
        else:
            self.clean_of_airports_table()


    def coord_filter_enabling(self):
        self.coord_lat_max.setEnabled(self.lat_chb.isChecked())
        self.coord_lat_min.setEnabled(self.lat_chb.isChecked())
        self.coord_long_max.setEnabled(self.long_chb.isChecked())
        self.coord_long_min.setEnabled(self.long_chb.isChecked())
        self.coord_filter_button.setEnabled(self.lat_chb.isChecked() or self.long_chb.isChecked())
        if self.lat_chb.isChecked():
            self.coord_validate(self.coord_lat_min,  self.coord_lat_max)
        else:
            ValidationClass.Validation.ErrorTxtBoxTemplateOff(self.coord_lat_min)
            ValidationClass.Validation.ErrorTxtBoxTemplateOff(self.coord_lat_max)

        if self.long_chb.isChecked():
            self.coord_validate(self.coord_long_min,  self.coord_long_max)
        else:
            ValidationClass.Validation.ErrorTxtBoxTemplateOff(self.coord_long_min)
            ValidationClass.Validation.ErrorTxtBoxTemplateOff(self.coord_long_max)

    def coord_validate_input_lag(self):
        self.input_timer.start(500)

    def coord_validate(self, min_widget, max_widget):
        try:
            if float(min_widget.text()) > float(max_widget.text()):
                ValidationClass.Validation.ErrorTxtBoxTemplateOn(min_widget, 'Minimum value must be lower than maximum value.\n The airport result will be empty')
                ValidationClass.Validation.ErrorTxtBoxTemplateOn(max_widget, 'Maximum value must be greater than minimum value.\n The airport result will be empty')
                test = QWidget()
            else:
                ValidationClass.Validation.ErrorTxtBoxTemplateOff(min_widget)
                ValidationClass.Validation.ErrorTxtBoxTemplateOff(max_widget)
        except Exception as e:
            ValidationClass.Validation.ErrorTxtBoxTemplateOff(min_widget)
            ValidationClass.Validation.ErrorTxtBoxTemplateOff(max_widget)
            return

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut and isinstance(obj, QLineEdit):
            self.empty_for_not_float(obj)
        return super().eventFilter(obj, event)

    def empty_for_not_float(self, sender):
        try: float(sender.text())
        except Exception as e: sender.setText('')


    def set_text(self):
        str = self.country_cbox.currentData()[1]
        str2 = self.city_cbox.currentData()[1]
        self.country_cbox.lineEdit().setText(str)
        self.city_cbox.lineEdit().setText(str2)

    def punkt_validate(self):
        sender = self.sender()
        ValidationClass.Validation.EmptyValueErrorComboBoxTemplate(sender)

    def get_airports_with_filters(self):
        city = 'city'
        country = 'country'
        latitude_min = '-2147483647'
        latitude_max = '2147483647'
        longitude_min = '-2147483647'
        longitude_max = '2147483647'

        if self.country_cbox.currentData() is None or self.city_cbox.currentData() is None: return

        if not self.country_cbox.currentData()[0] == -1: country = f"'{self.country_cbox.currentText()}'"
        if not self.city_cbox.currentData()[0] == -1: city  = f"'{self.city_cbox.currentText()}'"

        if self.lat_chb.isChecked():
            if self.coord_lat_min.text().strip() != "": latitude_min = f"'{self.coord_lat_min.text().strip().replace(',', '.')}'"
            if self.coord_lat_max.text().strip() != "": latitude_max = f"'{self.coord_lat_max.text().strip().replace(',', '.')}'"
        if self.long_chb.isChecked():
            if self.coord_long_min.text().strip() != "": latitude_min = f"'{self.coord_long_min.text().strip().replace(',', '.')}'"
            if self.coord_long_max.text().strip() != "": latitude_max = f"'{self.coord_long_max.text().strip().replace(',', '.')}'"

        query = ("SELECT id, name, city, country, ident_code, latitude, longitude FROM public.airports "
                 f"WHERE city = {city} AND country = {country} "
                 f"AND  latitude >= {latitude_min} AND  latitude <= {latitude_max} "
                 f"AND  longitude >= {longitude_min} AND  longitude <= {longitude_max} "
                 f"ORDER BY name ASC ")

        self.get_airports(query)


    def clean_of_airports_table(self):
        self.airport_grid_model.removeRows(0, self.airport_grid_model.rowCount())
        self.selected = 0
        self.all_items = 0
        self.refreshHeaders()



    def get_airports(self, query = None):
        db = DBConfig.getInstance()
        if db is not None:
            self.clean_of_airports_table()
            if not (query): query = "SELECT id, name, city, country, ident_code, latitude, longitude FROM public.airports ORDER BY name ASC"
            result = db.GetQueryResult(query)
            for row in result:
                items = []
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                checkbox_item.setEditable(False)
                items.append(checkbox_item)
                for value in row:
                    if type(value) is float:
                        f_intem = QStandardItem()
                        f_intem.setData(value, Qt.ItemDataRole.DisplayRole)
                        items.append(f_intem)
                    else:
                        items.append(QStandardItem(str(value)))
                self.airport_grid_model.appendRow(items)
                self.all_items = self.airport_grid_model.rowCount()
            self.refreshHeaders()


    def checkboxInGrid(self, item):
        if item.column() == 0:
            if item.checkState() == Qt.CheckState.Checked:
                self.selected += 1
                row_num = item.row()
                model = self.airport_grid_model
                selected_airport_id = model.item(row_num, 1).text()
                self.selected_airports.add(selected_airport_id)
            else:
                self.selected -= 1
                row_num = item.row()
                model = self.airport_grid_model
                selected_airport_id = model.item(row_num, 1).text()
                self.selected_airports.remove(selected_airport_id)


        self.refreshHeaders()



    def refreshHeaders(self):
        self.headers = [f"✓\n{self.selected} of {self.all_items}", "id", "Name", "City", "Country", "Code",
                        "Latitude", "Longitude"]
        self.airport_grid_model.setHorizontalHeaderLabels(self.headers)

    def comma_dot(self):
        sender = self.sender()
        text = sender.text()
        if ',' in text:
            sender.setText(text.replace(',', '.'))


    def LoadContries(self):

        if DBConfig.getInstance() is not None:
            try:
                query = "SELECT * FROM public.countries ORDER BY \"name\" ASC "
                query_res = DBConfig.getInstance().GetQueryResult(query)
                self.country_cbox.clear()
                any_country = (-1, "Any country")
                self.country_cbox.addItem(any_country[1], any_country)
                for country in query_res:
                    self.country_cbox.addItem(country[1] ,country)
                self.country_cbox.setCurrentIndex(0)


            except Exception as ex:
                QMessageBox.critical(self, "Error", f"Failed get countries from db: {str(ex)}", QMessageBox.StandardButton.Ok)


    def LoadCities(self):
        if DBConfig.getInstance() is not None:
            where = ''
            if self.country_cbox.currentData()[0] != -1: where = f'WHERE country_id = {self.country_cbox.currentData()[0]} '
            try:
                query = (f'SELECT * '
                         f'FROM public.cities as cit '
                         f'{where}'
                         f'ORDER BY NAME')
                query_res = DBConfig.getInstance().GetQueryResult(query)
                self.city_cbox.clear()
                any_city = (-1, "Any city")
                self.city_cbox.addItem(any_city[1], any_city)
                for city in query_res:
                    if city[1] is None or city[1] == '': continue
                    self.city_cbox.addItem(city[1], city)
                self.city_cbox.setCurrentIndex(0)
            except Exception as ex:
                QMessageBox.critical(self, "Error", f"Failed get cities from db: {str(ex)}",  QMessageBox.StandardButton.Ok)

    def GetSelectedData(self):
        return [self.selected_country_id, self.selected_city_id, self.selected_airports]





























