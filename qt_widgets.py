from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# noinspection PyUnresolvedReferences
import qrc_resources


class ExpandConstraint(QWidget):
    def __init__(self):
        super(ExpandConstraint, self).__init__()
        self.align = QWidget()
        self.align.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        self.align.setContentsMargins(0, 0, 0, 0)

        self.parent_layout = QHBoxLayout(self)
        self.parent_layout.addWidget(self.align)


class SeparatorLine(QWidget):
    def __init__(self):
        super(SeparatorLine, self).__init__()
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setContentsMargins(0, 0, 0, 0)

        self.parent_layout = QHBoxLayout(self)
        self.parent_layout.addWidget(self.line)


class SpinBox(QWidget):
    def __init__(self, label=""):
        super(SpinBox, self).__init__()
        self.parent_layout = QHBoxLayout(self)

        self.tag = QLabel()
        self.tag.setText(label)
        self.parent_layout.addWidget(self.tag)

        self.decrement = QPushButton()
        self.decrement.setIcon(QIcon(":arrow_left.svg"))
        self.parent_layout.addWidget(self.decrement)

        self.text_box = QLineEdit()
        self.parent_layout.addWidget(self.text_box)

        self.increment = QPushButton()
        self.increment.setIcon(QIcon(":arrow_right.svg"))
        self.parent_layout.addWidget(self.increment)

        self.lock = QPushButton()
        self.lock.setIcon(QIcon(":lock_closed.svg"))
        self.parent_layout.addWidget(self.lock)

        self.parent_layout.setContentsMargins(0, 0, 0, 0)


class PropertiesEdit(QWidget):
    def __init__(self, property_label=""):
        super(PropertiesEdit, self).__init__()

        self.properties_labels = ["X", "Y", "Z"]
        self.properties_widgets = [SpinBox(label) for label in self.properties_labels]

        self.property_label_layout = QVBoxLayout()
        self.property_label = QLabel(property_label)
        self.property_label_layout.addWidget(self.property_label)

        self.property_widgets_layout = QVBoxLayout()
        [self.property_widgets_layout.addWidget(widget) for widget in self.properties_widgets]

        self.parent_layout = QGridLayout(self)
        self.parent_layout.addLayout(self.property_label_layout, 0, 0)
        self.parent_layout.addLayout(self.property_widgets_layout, 0, 1)
        self.parent_layout.setColumnStretch(0, 1)
        self.parent_layout.setColumnStretch(1, 2)

        self.parent_layout.setContentsMargins(0, 0, 0, 0)


class RunWidget(QWidget):
    def __init__(self):
        super(RunWidget, self).__init__()
        self.parent_layout = QHBoxLayout(self)

        self.run_configs = QComboBox()
        self.run_configs.addItems(["Run all", "Convert voxels", "Texture voxels"])
        self.parent_layout.addWidget(self.run_configs)

        self.play = QPushButton()
        self.play.setIcon(QIcon(":play.svg"))
        self.parent_layout.addWidget(self.play)

        self.stop = QPushButton()
        self.stop.setIcon(QIcon(":stop.svg"))
        self.parent_layout.addWidget(self.stop)

        self.parent_layout.setContentsMargins(0, 0, 0, 0)
