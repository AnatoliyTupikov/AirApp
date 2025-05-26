from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QWindow, QFont, QMovie, QDoubleValidator
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QMainWindow, QWidget, QDialog, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QSpinBox, \
    QPushButton, QMessageBox

from DBconfig import DBConfig


class DBConfWindow(QDialog):
    def __init__(self, parent=None):
        super(DBConfWindow, self).__init__(parent)
        self.setWindowTitle("Dbconfig")

        self.setGeometry(100,100, 800, 600)
        self.setFixedSize(800, 600)
        self._block_close = False
        self.isValid = False


        main_layout = QVBoxLayout()
        title_label = QLabel("Database Configuration")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))


        hostname_container, self.hostname = self.UIField("IP or Hostname:", 600)

        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        port_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        port_layout.addWidget(port_label)
        self.port = QSpinBox()
        self.port.setFixedSize(100, 50)
        self.port.setFont(QFont("Arial", 13))
        self.port.setMinimum(1)
        self.port.setMaximum(65535)
        self.port.setValue(5432)
        port_layout.addWidget(self.port)
        port_container = QWidget()
        port_container.setLayout(port_layout)

        dBName_container, self.dbName = self.UIField("Database Name:", 600)
        username_container, self.username = self.UIField("Username:", 300)
        password_container, self.password = self.UIField("Password:", 300)


        buttons_layout = QHBoxLayout()

        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedSize(100, 60)
        self.connect_button.clicked.connect(self.setConfig)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(100, 60)
        cancel_button.clicked.connect(self.close)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(self.connect_button)


        buttons_container = QWidget()
        buttons_container.setLayout(buttons_layout)






        main_layout.addWidget(title_label)
        main_layout.addWidget(hostname_container, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(port_container, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(dBName_container, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(username_container, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(password_container, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(buttons_container, alignment=Qt.AlignmentFlag.AlignRight)

        self.load_label = QLabel(self)
        self.load_label.setFixedSize(200, 200)

        self.animation = QMovie("Source//loading.gif")
        self.animation.setScaledSize(self.load_label.size())
        self.load_label.setMovie(self.animation)
        self.load_label.setStyleSheet("background: transparent;")
        self.load_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.load_label.hide()

        self.setLayout(main_layout)
        self.load_label.raise_()


        if parent.db is not None:
            self.hostname.setText(parent.db.hostname)
            self.port.setValue(parent.db.port)
            self.username.setText(parent.db.username)
            self.password.setText(parent.db.password)
            self.dbName.setText(parent.db.database)

    def closeEvent(self, event):
        if self._block_close:
            event.ignore()  # Блокируем закрытие окна
        else:
            event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            parent_geom = self.parent().geometry()
            x = parent_geom.x() + (parent_geom.width() - self.width()) // 2
            y = parent_geom.y() + (parent_geom.height() - self.height()) // 2
            self.move(x, y)
        self.CheckAllTxtBoxes()



    def UIField (self, label_txt, line_weight):
        elem_layout = QHBoxLayout()
        elem_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        elem_label = QLabel(f"{label_txt}")
        elem_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        elem_layout.addWidget(elem_label)
        elem_lin_edit = QLineEdit()
        elem_lin_edit.setToolTip(elem_lin_edit.text())
        elem_lin_edit.textChanged.connect(self.editingValidation)
        elem_lin_edit.setFixedSize(line_weight, 35)
        elem_lin_edit.setStyleSheet("padding-left: 10px;")
        elem_lin_edit.setFont(QFont("Arial", 10))
        elem_layout.addWidget(elem_lin_edit)
        elem_container = QWidget()
        elem_container.setLayout(elem_layout)
        return elem_container, elem_lin_edit

    def GetDBconfig(self):
        db = DBConfig()
        db.hostname = self.hostname.text()
        db.port = self.port.value()
        db.database = self.dbName.text()
        db.username = self.username.text()
        db.password = self.password.text()

        return db

    def SaveDbToConfig(self, dbconfig):
        try:
            dbconfig.CheckDbConnection()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed connect to DB: {str(e)}",
                                 QMessageBox.StandardButton.Ok)
            return
        try:
            DBConfig.SetDbConfigToConfig(self.parent().confpath,dbconfig)
            self.parent().db = dbconfig
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed save the DB configuration: {str(e)}",
                                 QMessageBox.StandardButton.Ok)
            return
        QMessageBox.information(self, "Success", "Connection established")

    def setConfig(self):
        x = (self.width() - self.load_label.width()) // 2
        y = (self.height() - self.load_label.height()) // 2

        self.load_label.move(x, y)
        self.animation.start()
        self.setEnabled(False)
        self._block_close = True
        self.load_label.show()

        QTest.qWait(2000)
        self.SaveDbToConfig(self.GetDBconfig())

        self.setEnabled(True)
        self._block_close = False
        self.load_label.hide()

    def editingValidation(self):
        sender = self.sender()
        if sender.text() == "" or sender.text() is None:
            sender.setStyleSheet("border: 2px solid red;")
            sender.setToolTip("Value cannot be null")
        else:
            sender.setStyleSheet("border: 1px solid black;")
            sender.setToolTip(sender.text())
        self.CheckAllTxtBoxes()


    def CheckAllTxtBoxes(self):
        all_fields = all(field.text().strip() != "" for field in self.findChildren(QLineEdit))
        self.connect_button.setEnabled(all_fields)

