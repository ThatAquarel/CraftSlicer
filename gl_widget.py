import sys

import numpy as np
import pyrr.matrix44
import stl
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *

from gl_elements import GlModel, GlImage, GlGrid
from gl_processor import display_setup


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(1280, 720)

        self.gl_widget = GlWidget()
        self.gl_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        parent_layout = QHBoxLayout()
        parent_layout.addWidget(self.gl_widget)

        widget = QWidget()
        widget.setLayout(parent_layout)
        self.setCentralWidget(widget)

        self.show()


class GlWidget(QGLWidget):
    def __init__(self, *__args):
        super().__init__(*__args)
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

    def resizeGL(self, width: int, height: int):
        if height <= 0 or width <= 0:
            return

        glViewport(0, 0, width, height)
        projection_ = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 10000)
        glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, projection_)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.grid.draw()
        for model in self.models:
            model.draw()
        for image in self.images:
            image.draw()

        glFlush()

        glUseProgram(0)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glViewport(0, 0, self.width(), self.height())
        gluOrtho2D(0, self.width(), 0, self.height())

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glColor3f(1.0, 0.0, 0.0)

        transformation_matrix = self.models[0].transformation_matrix
        x, y, z, _ = transformation_matrix @ [1., 1., 1., 0.]
        x, y = x + self.width() / 2, y + self.height() / 2

        translate = [self.translate[i] / ([940, 625][i] / 2) for i in range(2)]
        x, y = x + self.width() * -translate[1], y + self.height() * -translate[0]

        glBegin(GL_QUADS)

        glVertex2f(x, y)
        glVertex2f(x, y + 100)
        glVertex2f(x + 100, y + 100)
        glVertex2f(x + 100, y)

        glEnd()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glFlush()

        glUseProgram(self.shader)

    def initializeGL(self):
        model_mesh = stl.mesh.Mesh.from_file(".\\models\\statue.stl")
        self.models.append(GlModel(model_mesh.vectors, self))

        self.grid = GlGrid(self)

        from PIL import Image
        image = Image.open(".\\models\\statue.png")
        self.images.append(GlImage(image, self))

        self.model_loc, self.proj_loc, self.view_loc, self.shader = display_setup(*self.grid.maxes)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    app.exec_()
