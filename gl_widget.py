import os
import sys

import numpy as np
import pyrr.matrix44
from OpenGL.GL import *
from PyQt5.QtCore import Qt, QThreadPool, QMutex
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *

# noinspection PyUnresolvedReferences
import qrc_resources
from gl_elements import GlModel, GlImage, GlGrid
from gl_processor import display_setup
from qt_threads import ImportRunnable


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(1280, 720)

        self.gl_widget = GlWidget(self)
        self.gl_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        parent_layout = QHBoxLayout()
        parent_layout.addWidget(self.gl_widget)

        widget = QWidget()
        widget.setLayout(parent_layout)
        self.setCentralWidget(widget)

        self.show()


class GlWidget(QGLWidget):
    def __init__(self, window, *__args):
        super().__init__(*__args)
        self.window = window

        self.theta = [np.pi / 2, np.pi, 0]
        self.theta_ = [np.pi / 2, np.pi, 0]

        self.translate = [0, 0]
        self.translate_ = [0, 0]

        self.zoom = -6

        self.mouse = [0, 0]
        self.vector = [0, 0]
        self.is_rotate = False
        self.is_translate = False

        self.model_loc, self.proj_loc, self.view_loc, self.shader = None, None, None, None
        self.models = []
        self.images = []
        self.grid = None

        self.setAcceptDrops(True)
        self.thread_pool = QThreadPool.globalInstance()

        self.buffer_mutex = QMutex()
        self.buffer_mutex.lock()
        self.model_buffer = []
        self.image_buffer = []
        self.buffer_mutex.unlock()

    def update_view(self):
        view = pyrr.matrix44.create_look_at(pyrr.Vector3([self.grid.maxes[1] * self.zoom,
                                                          self.translate[0], self.translate[1]]),
                                            pyrr.Vector3([0, self.translate[0], self.translate[1]]),
                                            pyrr.Vector3([0, 1, 0]))
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, view)

    def normalize_mouse_coords(self, a0):
        a_min = min([self.frameSize().width() / 2, self.frameSize().height() / 2])
        norm_x = (a0.x() - self.frameSize().width() / 2) / a_min
        norm_y = (a0.y() - self.frameSize().height() / 2) / -a_min

        return norm_x, norm_y

    def mouseMoveEvent(self, a0: QMouseEvent):
        norm_x, norm_y = self.normalize_mouse_coords(a0)
        self.vector = [norm_x - self.mouse[0], norm_y - self.mouse[1]]

        if self.is_rotate:
            self.theta[1] = self.theta_[1] - self.vector[0]
            self.theta[2] = self.theta_[2] + self.vector[1]

        elif self.is_translate:
            self.translate[0] = self.translate_[0] - self.vector[1] * 100
            self.translate[1] = self.translate_[1] - self.vector[0] * 100

            self.update_view()

        self.update()

    def mousePressEvent(self, a0: QMouseEvent):
        self.mouse = self.normalize_mouse_coords(a0)

        if a0.button() == Qt.MouseButton.RightButton:
            self.is_rotate = True
            self.theta_ = [rad for rad in self.theta]

        elif a0.button() == Qt.MouseButton.MiddleButton:
            self.is_translate = True
            self.translate_ = [vec for vec in self.translate]

    def mouseReleaseEvent(self, a0: QMouseEvent):
        if self.is_rotate:
            self.is_rotate = False
            self.theta_ = [rad for rad in self.theta]

        elif self.is_translate:
            self.is_translate = False
            self.translate_ = [vec for vec in self.translate]

        self.mouse = [0, 0]
        self.vector = [0, 0]

    def wheelEvent(self, a0: QWheelEvent):
        self.zoom = max(-32., min(-1e-4, self.zoom + -a0.angleDelta().y() / 120))
        self.update_view()
        self.update()

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            files = [file.toLocalFile() for file in e.mimeData().urls() if
                     file.toLocalFile().split(".")[1] in ["stl", "png", "jpg"]]
            if files:
                e.accept()
                return
        e.ignore()

    def dropEvent(self, e: QDropEvent):
        self.thread_pool.start(ImportRunnable(self, e.mimeData().urls()))

    def resizeGL(self, width: int, height: int):
        if height <= 0 or width <= 0:
            return

        glViewport(0, 0, width, height)
        projection_ = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 10000)
        glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, projection_)

    def paintGL(self):
        if self.model_buffer or self.image_buffer:
            self.buffer_mutex.lock()

            if self.model_buffer:
                for model in self.model_buffer:
                    model.gl_calls()
                    self.models.append(model)
                self.model_buffer = []
            if self.image_buffer:
                for image in self.image_buffer:
                    image.gl_calls()
                    self.images.append(image)
                self.image_buffer = []

            self.buffer_mutex.unlock()

            self.update_item_tree()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.grid.draw()
        for model in self.models:
            model.draw()
        for image in self.images:
            image.draw()

        glFlush()

    def initializeGL(self):
        self.models.append(GlModel(".\\models\\statue.stl", self))
        [model.gl_calls() for model in self.models]

        self.grid = GlGrid(self, maxes=[80, 80, 160])

        self.images.append(GlImage(".\\models\\statue.png", self))
        [image.gl_calls() for image in self.images]

        self.model_loc, self.proj_loc, self.view_loc, self.shader = display_setup(*self.grid.maxes)

        self.update_item_tree()

    def update_item_tree(self):
        items = [QTreeWidgetItem([category]) for category in ["Models", "Textures"]]
        for model in self.models:
            child = QTreeWidgetItem([os.path.basename(model.file)])
            child.setIcon(0, QIcon(":model.svg"))
            items[0].addChild(child)
        for image in self.images:
            child = QTreeWidgetItem([os.path.basename(image.file)])
            child.setIcon(0, QIcon(":image.svg"))
            items[1].addChild(child)

        self.window.tree.clear()
        self.window.tree.insertTopLevelItems(0, items)
        self.window.tree.expandAll()
        self.window.tree.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = MainWindow()
    app.exec_()
