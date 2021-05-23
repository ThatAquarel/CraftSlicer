from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.gl_widget = GlWidget(self)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.gl_widget)
        self.setLayout(main_layout)


class GlWidget(QGLWidget):
    def __init__(self, _, *__args):
        super().__init__(*__args)
        self.setMinimumSize(640, 480)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        print("%i %i" % (a0.x(), a0.y()))

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(-2.5, 0.5, -6.0)
        glColor3f(1.0, 1.5, 0.0)
        glPolygonMode(GL_FRONT, GL_FILL)
        glBegin(GL_TRIANGLES)
        glVertex3f(2.0, -1.2, 0.0)
        glVertex3f(2.6, 0.0, 0.0)
        glVertex3f(2.9, -1.2, 0.0)
        glEnd()
        glFlush()

    def initializeGL(self):
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, 1.33, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)


if __name__ == '__main__':
    app = QApplication(["Test"])
    window = MainWindow()
    window.show()
    app.exec_()
