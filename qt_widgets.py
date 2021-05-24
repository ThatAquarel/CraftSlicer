from PyQt5.QtCore import pyqtSignal
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


# noinspection PyUnresolvedReferences
class SpinBox(QWidget):
    value_edited = pyqtSignal(str, float)

    def __init__(self, label="", default_value=0, button_step=0.1):
        super(SpinBox, self).__init__()
        self.value = default_value
        self.value_label = label
        self.button_step = button_step

        self.parent_layout = QHBoxLayout(self)

        self.tag = QLabel()
        self.tag.setText(label)
        self.parent_layout.addWidget(self.tag)

        self.decrement = QPushButton()
        self.decrement.clicked.connect(self.decrement_signal)
        self.decrement.setIcon(QIcon(":arrow_left.svg"))
        self.parent_layout.addWidget(self.decrement)

        self.text_box = QLineEdit()
        self.update_text_box()
        self.text_box.textEdited.connect(self.text_edited)
        self.text_box.setValidator(QDoubleValidator(-1024., 1024., 3))
        self.parent_layout.addWidget(self.text_box)

        self.increment = QPushButton()
        self.increment.clicked.connect(self.increment_signal)
        self.increment.setIcon(QIcon(":arrow_right.svg"))
        self.parent_layout.addWidget(self.increment)

        self.lock = QPushButton()
        self.lock.setIcon(QIcon(":lock_closed.svg"))
        self.parent_layout.addWidget(self.lock)

        self.parent_layout.setContentsMargins(0, 0, 0, 0)

    def update_text_box(self):
        self.text_box.setText("%0.3f" % self.value)

    def text_edited(self, text: str):
        try:
            self.value = float(text)
        except ValueError:
            self.value = 0.

        self.value_edited.emit(self.value_label, self.value)

    def increment_signal(self):
        self.value += self.button_step
        self.update_text_box()
        self.value_edited.emit(self.value_label, self.value)

    def decrement_signal(self):
        self.value -= self.button_step
        self.update_text_box()
        self.value_edited.emit(self.value_label, self.value)


class PropertiesEdit(QWidget):
    def __init__(self, property_label="", default_value=0, button_step=0.1):
        super(PropertiesEdit, self).__init__()
        self.properties_widgets = {label: SpinBox(label, default_value, button_step) for label in ["X", "Y", "Z"]}

        self.property_label_layout = QVBoxLayout()
        self.property_label = QLabel(property_label)
        self.property_label_layout.addWidget(self.property_label)

        self.property_widgets_layout = QVBoxLayout()
        [self.property_widgets_layout.addWidget(widget) for _, widget in self.properties_widgets.items()]

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
        # self.run_configs.addItems(["Run all", "Convert voxels", "Texture voxels"])
        self.run_configs.addItems(["Convert voxels", "Texture voxels"])
        self.parent_layout.addWidget(self.run_configs)

        self.play = QPushButton()
        self.play.setIcon(QIcon(":play.svg"))
        self.parent_layout.addWidget(self.play)

        self.parent_layout.setContentsMargins(0, 0, 0, 0)
