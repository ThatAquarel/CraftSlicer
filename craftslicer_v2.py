import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gl_widget import GlWidget

# noinspection PyUnresolvedReferences
import breeze_resources
# noinspection PyUnresolvedReferences
import qrc_resources


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(1280, 720)

        self._create_actions()
        self._create_menu_bar()
        self._create_toolbars()

        self.canvas = GlWidget()
        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._create_left_layout()
        self._create_right_layout()

        grid_layout1 = QGridLayout()
        grid_layout1.addWidget(self.top_tabs, 0, 0)
        grid_layout1.addWidget(self.bottom_tabs, 1, 0)
        grid_layout1.setRowStretch(0, 3)
        grid_layout1.setRowStretch(1, 1)

        grid_layout2 = QGridLayout()
        grid_layout2.addWidget(self.tree, 0, 0)
        grid_layout2.addWidget(self.properties_tab, 1, 0)
        grid_layout2.setRowStretch(0, 2)
        grid_layout2.setRowStretch(1, 2)

        parent_layout = QGridLayout()
        parent_layout.addLayout(grid_layout1, 0, 0)
        parent_layout.addLayout(grid_layout2, 0, 1)
        parent_layout.setColumnStretch(0, 3)
        parent_layout.setColumnStretch(1, 1)

        widget = QWidget()
        widget.setLayout(parent_layout)
        self.setCentralWidget(widget)

        self.show()

        # self.canvas.render.draw(self.model_tab.contentsRect().width(), self.model_tab.contentsRect().height())

    def _create_left_layout(self):
        self.top_tabs = QTabWidget()
        self.model_tab = QWidget()
        self.voxel_tab = QWidget()

        self.bottom_tabs = QTabWidget()
        self.graph_tab = QWidget()
        self.console_tab = QWidget()

        model_tab_layout = QHBoxLayout()
        model_tab_layout.addWidget(self.canvas)
        self.model_tab.setLayout(model_tab_layout)

        self.top_tabs.addTab(self.model_tab, "Model")
        self.top_tabs.addTab(self.voxel_tab, "Voxel")

        self.bottom_tabs.addTab(self.graph_tab, "Graph")
        self.bottom_tabs.addTab(self.console_tab, "Console")

    def _create_right_layout(self):
        data = {"Project A": ["file_a.py", "file_a.txt", "something.xls"],
                "Project B": ["file_b.csv", "photo.jpg"],
                "Project C": []}
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Name", "Type"])
        items = []
        for key, values in data.items():
            item = QTreeWidgetItem([key])
            for value in values:
                ext = value.split(".")[-1].upper()
                child = QTreeWidgetItem([value, ext])
                item.addChild(child)
            items.append(item)
        self.tree.insertTopLevelItems(0, items)
        self.tree.resize(self.tree.sizeHint())

        self.properties_tab = QTabWidget()
        self.obj_properties_tab = QWidget()
        self.mat_properties_tab = QWidget()

        self.properties_tab.addTab(self.obj_properties_tab, "Object Properties")
        self.properties_tab.addTab(self.mat_properties_tab, "Material Properties")

    def _create_actions(self):
        self.new_action = QAction(QIcon(":new.svg"), "&New", self)
        self.open_action = QAction(QIcon(":open.svg"), "&Open", self)
        self.save_action = QAction(QIcon(":save.svg"), "&Save", self)
        self.select_action = QAction(QIcon(":select.svg"), "&Select", self)
        self.move_action = QAction(QIcon(":move.svg"), "&Move", self)
        self.rotate_action = QAction(QIcon(":rotate.svg"), "&Rotate", self)
        self.scale_action = QAction(QIcon(":scale.svg"), "&Scale", self)
        self.mirror_action = QAction(QIcon(":mirror.svg"), "&Mirror", self)
        self.about_action = QAction(QIcon(":about.svg"), "&About", self)
        self.exit_action = QAction(QIcon(":exit.svg"), "&Exit", self)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.select_action)
        edit_menu.addAction(self.move_action)
        edit_menu.addAction(self.rotate_action)
        edit_menu.addAction(self.scale_action)
        edit_menu.addAction(self.mirror_action)

        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(self.about_action)

    def _create_toolbars(self):
        file_toolbar = self.addToolBar("File")
        file_toolbar.setMovable(False)
        file_toolbar.addAction(self.new_action)
        file_toolbar.addAction(self.open_action)
        file_toolbar.addAction(self.save_action)

        edit_toolbar = self.addToolBar("Edit")
        edit_toolbar.setMovable(False)
        edit_toolbar.addAction(self.select_action)
        edit_toolbar.addAction(self.move_action)
        edit_toolbar.addAction(self.rotate_action)
        edit_toolbar.addAction(self.scale_action)
        edit_toolbar.addAction(self.mirror_action)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    file = QFile(":/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    w = MainWindow()
    app.exec_()
