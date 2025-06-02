class Validation:

    @staticmethod
    def ErrorTxtBoxTemplateOn(sender, error_text):
            sender.setStyleSheet("border: 2px solid red;")
            sender.setToolTip(error_text)

    @staticmethod
    def ErrorTxtBoxTemplateOff(sender):
        sender.setStyleSheet("")
        sender.setToolTip(sender.text())



    @staticmethod
    def EmptyValueErrorComboBoxTemplate(sender):
        if sender.currentData() == "" or sender.currentData() is None:
            sender.setStyleSheet("border: 2px solid red;")
            sender.setToolTip("Value cannot be null")
        else:
            sender.setStyleSheet("")

