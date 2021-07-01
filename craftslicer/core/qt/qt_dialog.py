import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from craftslicer.core.mc.palette_list import palette_list


class AssignBlocksDialog(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Cancel)

        self.parent_layout = QGridLayout()
        self.parent_layout.addWidget(QLabel("Select Minecraft Version"), 0, 0)
        # self.layout().addWidget(QLabel("Select Minecraft Version"))

        self.version_list = QComboBox()
        self.version_list.addItems(palette_list.keys())
        self.parent_layout.addWidget(self.version_list, 0, 1)
        # self.layout().addWidget(self.version_list)
        self.layout().addLayout(self.parent_layout, 0, 0)

        self.setWindowTitle("Assign Blocks")

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)


class DeployBlocksDialog(QMessageBox):
    def __init__(self):
        super(DeployBlocksDialog, self).__init__()

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Cancel)

        self.parent_layout = QGridLayout()
        self.parent_layout.addWidget(QLabel("Author"), 0, 0)
        self.author_text = QLineEdit()
        self.parent_layout.addWidget(self.author_text, 0, 1)

        self.parent_layout.addWidget(QLabel("Project Name"), 1, 0)
        self.project_text = QLineEdit()
        self.parent_layout.addWidget(self.project_text, 1, 1)

        self.parent_layout.setColumnStretch(0, 1)
        self.parent_layout.setColumnStretch(1, 3)

        self.layout().addLayout(self.parent_layout, 0, 0)

        self.setWindowTitle("Deploy Blocks")

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(128, 128)

        self.show()

        dialog = DeployBlocksDialog()
        ret = dialog.exec_()

        if ret == QMessageBox.Cancel or ret == QMessageBox.Close or ret == QMessageBox.Ok:
            exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = MainWindow()
    app.exec_()
