import sys

import matplotlib
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from render import Render

matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.parent = parent
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        from models import house
        vertices, faces = house

        self.render = Render(vertices, faces, self.fig)
        self.fig.axes[0].get_xaxis().set_visible(False)
        self.fig.axes[0].get_yaxis().set_visible(False)
        super(MplCanvas, self).__init__(self.fig)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        canvas = MplCanvas(self, width=5, height=4, dpi=100)

        self.on_press = canvas.render.on_press
        self.on_release = canvas.render.on_release
        self.on_move = canvas.render.on_move
        canvas.mpl_connect('button_press_event', self.on_press)
        canvas.mpl_connect('button_release_event', self.on_release)
        canvas.mpl_connect('motion_notify_event', self.on_move)

        self.setCentralWidget(canvas)

        toolbar = NavigationToolbar(canvas, self)

        parent_layout = QtWidgets.QHBoxLayout()
        plot_layout = QtWidgets.QVBoxLayout()
        plot_layout.addWidget(toolbar)
        plot_layout.addWidget(canvas)
        parent_layout.addLayout(plot_layout)

        data = {"Project A": ["file_a.py", "file_a.txt", "something.xls"],
                "Project B": ["file_b.csv", "photo.jpg"],
                "Project C": []}
        tree = QtWidgets.QTreeWidget()
        tree.setColumnCount(2)
        tree.setHeaderLabels(["Name", "Type"])
        items = []
        for key, values in data.items():
            item = QtWidgets.QTreeWidgetItem([key])
            for value in values:
                ext = value.split(".")[-1].upper()
                child = QtWidgets.QTreeWidgetItem([value, ext])
                item.addChild(child)
            items.append(item)
        tree.insertTopLevelItems(0, items)

        parent_layout.addWidget(tree)

        widget = QtWidgets.QWidget()
        widget.setLayout(parent_layout)
        self.setCentralWidget(widget)
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()
