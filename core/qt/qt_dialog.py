from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.mc.palette_list import palette_list


class AssignBlocksDialog(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Cancel)

        self.layout().addWidget(QLabel("Select Minecraft Version"))

        self.version_list = QComboBox()
        self.version_list.addItems(palette_list.keys())
        self.layout().addWidget(self.version_list)

        self.setWindowTitle("Assign Blocks")

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
