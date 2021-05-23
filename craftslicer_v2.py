import sys

import qdarkstyle
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# noinspection PyUnresolvedReferences
import qrc_resources
from gl_widget import GlWidget
from qt_widgets import PropertiesEdit, ExpandConstraint, SeparatorLine


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(1280, 720)

        self._create_actions()
        self._create_menu_bar()
        self._create_toolbars()

        self.canvas = GlWidget(self)
        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._create_left_layout()
        self._create_right_layout()

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.tree, 0, 0)
        grid_layout.addWidget(self.properties_tabs, 1, 0)
        # grid_layout.addWidget(self.properties_tabs, 0, 0)
        # grid_layout.addWidget(self.tree, 1, 0)
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)

        parent_layout = QGridLayout()
        parent_layout.addWidget(self.render_tabs, 0, 0)
        parent_layout.addLayout(grid_layout, 0, 1)
        parent_layout.setColumnStretch(0, 4)
        parent_layout.setColumnStretch(1, 1)

        widget = QWidget()
        widget.setLayout(parent_layout)
        self.setCentralWidget(widget)

        self.show()

    def _create_left_layout(self):
        self.render_tabs = QTabWidget()
        self.model_tab = QWidget()
        self.voxel_tab = QWidget()

        model_tab_layout = QHBoxLayout()
        model_tab_layout.addWidget(self.canvas)
        model_tab_layout.addWidget(self.edit_toolbar)
        self.edit_toolbar.show()
        self.edit_toolbar.setOrientation(Qt.Vertical)
        self.model_tab.setLayout(model_tab_layout)

        self.render_tabs.addTab(self.model_tab, "Model")
        self.render_tabs.addTab(self.voxel_tab, "Voxel")

    def _create_right_layout(self):
        data = {"Project A": ["file_a.py", "file_a.txt", "something.xls"],
                "Project B": ["file_b.csv", "photo.jpg"],
                "Project C": []}
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Scene"])
        items = []
        for key, values in data.items():
            item = QTreeWidgetItem([key])
            for value in values:
                # ext = value.split(".")[-1].upper()
                child = QTreeWidgetItem([value])
                item.addChild(child)
            items.append(item)
        self.tree.insertTopLevelItems(0, items)

        self.properties_tabs = QTabWidget()
        self.properties_tabs.setTabPosition(QTabWidget.TabPosition.South)
        self.obj_properties_tab = QWidget()
        self.obj_properties_tab_layout = QVBoxLayout()

        self.obj_properties_tab_layout.addWidget(PropertiesEdit("Location"))
        self.obj_properties_tab_layout.addWidget(SeparatorLine())
        self.obj_properties_tab_layout.addWidget(PropertiesEdit("Rotation"))
        self.obj_properties_tab_layout.addWidget(SeparatorLine())
        self.obj_properties_tab_layout.addWidget(PropertiesEdit("Scale"))
        self.obj_properties_tab_layout.addWidget(ExpandConstraint())
        self.obj_properties_tab.setLayout(self.obj_properties_tab_layout)

        self.mat_properties_tab = QWidget()

        self.properties_tabs.addTab(self.obj_properties_tab, "Object Properties")
        self.properties_tabs.addTab(self.mat_properties_tab, "Material Properties")

    def _create_actions(self):
        self.new_action = QAction(QIcon(":new.svg"), "&New", self)
        self.open_action = QAction(QIcon(":open.svg"), "&Open", self)
        self.save_action = QAction(QIcon(":save.svg"), "&Save", self)
        self.exit_action = QAction(QIcon(":exit.svg"), "&Exit", self)

        self.select_action = QAction(QIcon(":select.svg"), "&Select", self)
        self.move_action = QAction(QIcon(":move.svg"), "&Move", self)
        self.rotate_action = QAction(QIcon(":rotate.svg"), "&Rotate", self)
        self.scale_action = QAction(QIcon(":scale.svg"), "&Scale", self)
        self.mirror_action = QAction(QIcon(":mirror.svg"), "&Mirror", self)

        self.pan_action = QAction(QIcon(":pan.svg"), "&Pan", self)
        self.view_action = QAction(QIcon(":view.svg"), "&Rotate", self)
        self.zoom_action = QAction(QIcon(":zoom.svg"), "&Zoom", self)

        self.about_action = QAction(QIcon(":about.svg"), "&About", self)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.pan_action)
        edit_menu.addAction(self.view_action)
        edit_menu.addAction(self.zoom_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_action)
        edit_menu.addAction(self.move_action)
        edit_menu.addAction(self.rotate_action)
        edit_menu.addAction(self.scale_action)
        edit_menu.addAction(self.mirror_action)

        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(self.about_action)

    def _create_toolbars(self):
        self.edit_toolbar = self.addToolBar("Edit")
        self.removeToolBar(self.edit_toolbar)

        self.edit_toolbar.setMovable(False)
        self.edit_toolbar.addAction(self.pan_action)
        self.edit_toolbar.addAction(self.view_action)
        self.edit_toolbar.addAction(self.zoom_action)
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addAction(self.select_action)
        self.edit_toolbar.addAction(self.move_action)
        self.edit_toolbar.addAction(self.rotate_action)
        self.edit_toolbar.addAction(self.scale_action)
        self.edit_toolbar.addAction(self.mirror_action)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

    window = MainWindow()
    app.exec_()
