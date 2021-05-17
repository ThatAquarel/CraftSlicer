import sys

import pyrr.matrix44
import stl
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *

from gl_processor import *


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(1280, 720)

        self.gl_widget = GlWidget()

        parent_layout = QHBoxLayout()
        parent_layout.addWidget(self.gl_widget)

        widget = QWidget()
        widget.setLayout(parent_layout)
        self.setCentralWidget(widget)

        self.show()


# noinspection DuplicatedCode
class GlWidget(QGLWidget):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.theta = [np.pi / 2, 0, 0]
        # self.theta = [0, 0, 0]
        self.translate = [0, 0, 0]

        self.theta_ = [np.pi / 2, 0, 0]
        # self.theta_ = [0, 0, 0]
        self.translate_ = [0, 0, 0]
        self.mouse_ = [0, 0]
        self.vector_ = [0, 0]

        self.press = False

        self.face_vertices, self.line_vertices, self.vertices, self.indices = None, None, None, None
        self.grid_vertices, self.grid_indices = None, None

        self.model_loc, self.proj_loc, self.position = None, None, None
        self.vao, self.vbo, self.ebo = None, None, None

    def normalize_mouse_coords(self, a0):
        a_min = min([self.frameSize().width() / 2, self.frameSize().height() / 2])
        norm_x = (a0.x() - self.frameSize().width() / 2) / a_min
        norm_y = (a0.y() - self.frameSize().height() / 2) / -a_min

        return norm_x, norm_y

    def mouseMoveEvent(self, a0: QMouseEvent):
        if not self.press:
            return

        norm_x, norm_y = self.normalize_mouse_coords(a0)

        self.vector_ = [norm_x - self.mouse_[0], norm_y - self.mouse_[1]]

        self.theta[1] = self.theta_[1] - self.vector_[0]

        # self.theta[0] = self.theta_[0] + np.sin(self.vector_[1])
        # self.theta[2] = self.theta_[2] + np.cos(self.vector_[1])

        self.update()

    def mousePressEvent(self, a0: QMouseEvent):
        if self.press:
            return
        self.press = True

        self.theta_ = [rad for rad in self.theta]
        self.translate_ = [vec for vec in self.translate]

        self.mouse_ = self.normalize_mouse_coords(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent):
        if not self.press:
            return
        self.press = False

        self.theta_ = [rad for rad in self.theta]
        self.translate_ = [vec for vec in self.translate]

        self.mouse_ = [0, 0]
        self.vector_ = [0, 0]

    def resizeGL(self, width: int, height: int):
        glViewport(0, 0, width, height)
        projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 10000)
        glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, projection)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # translate = pyrr.matrix44.create_from_translation(pyrr.Vector3([-30, 0, -30]))
        def x_rotate(theta):
            c, s = np.cos(theta), np.sin(theta)
            return np.array([[1, 0, 0, 0], [0, c, -s, 0],
                             [0, s, c, 0], [0, 0, 0, 1]], dtype=float)

        def y_rotate(theta):
            c, s = np.cos(theta), np.sin(theta)
            return np.array([[c, 0, s, 0], [0, 1, 0, 0],
                             [-s, 0, c, 0], [0, 0, 0, 1]], dtype=float)

        def z_rotate(theta):
            c, s = np.cos(theta), np.sin(theta)
            return np.array([[c, -s, 0, 0], [s, c, 0, 0],
                             [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)

        rot_x = pyrr.Matrix44.from_x_rotation(self.theta[0])
        rot_y = pyrr.Matrix44.from_y_rotation(self.theta[1])
        rot_z = pyrr.Matrix44.from_z_rotation(self.theta[2])

        # rot_x = x_rotate(self.theta[0])
        # rot_y = y_rotate(self.theta[1])
        # rot_z = z_rotate(self.theta[2])

        # transformation_matrix = rot_x @ rot_y @ rot_z @ self.position
        transformation_matrix = rot_x @ rot_y @ rot_z @ self.position
        # transformation_matrix = self.position

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glBindVertexArray(self.vao[2])
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, transformation_matrix)
        glLineWidth(2)
        glDrawElements(GL_LINES, len(self.grid_indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(self.vao[1])
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, transformation_matrix)
        glLineWidth(1)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBindVertexArray(self.vao[0])
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, transformation_matrix)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
        glFlush()

    def initializeGL(self):
        model_mesh = stl.mesh.Mesh.from_file(".\\models\\statue.stl")
        face_vertices, face_indices = vector_to_vertex_index(model_mesh.vectors)

        self.face_vertices, self.line_vertices, self.vertices, self.indices = vertex_index_to_gl(face_vertices,
                                                                                                 face_indices)
        self.grid_vertices, self.grid_indices = grid_gl(*np.amax(self.vertices, axis=0))
        self.vao, self.vbo, self.ebo = create_vao(
            [self.face_vertices, self.indices],
            [self.line_vertices, self.indices],
            [self.grid_vertices, self.grid_indices])

        self.model_loc, self.proj_loc, self.position = display_setup(*np.amax(self.vertices, axis=0))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    app.exec_()
