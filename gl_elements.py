import os

import numpy as np
import stl
from PIL import Image

from gl_processor import *


class GlModel:
    def __init__(self, file, widget):
        self.file = file
        self.filename = os.path.basename(self.file)
        self.model_mesh = stl.mesh.Mesh.from_file(file)

        self.theta = [0, 0, 0]
        self.position = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.widget = widget

        self.face_vertices, self.line_vertices, self.vertices, self.indices = vector_gl(self.model_mesh.vectors)
        self.maxes = np.amax(self.vertices, axis=0)

        self.vao, self.vbo, self.ebo = None, None, None

        self.transformation_matrix = None
        self.set_transformation_matrix()

        self.visible = True

    def gl_calls(self):
        self.vao, self.vbo, self.ebo = create_vao(
            [self.face_vertices, self.indices],
            [self.line_vertices, self.indices])

    def set_transformation_matrix(self):
        self.transformation_matrix = position_matrix(self.theta, self.position, self.scale, reverse=True) \
                                     @ position_matrix(self.widget.theta, [0., 0., 0.], [1., 1., 1.])

    def draw(self):
        self.set_transformation_matrix()

        if not self.visible:
            return

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBindVertexArray(self.vao[0])
        glUniformMatrix4fv(self.widget.model_loc, 1, GL_FALSE, self.transformation_matrix)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBindVertexArray(self.vao[1])
        glUniformMatrix4fv(self.widget.model_loc, 1, GL_FALSE, self.transformation_matrix)
        glLineWidth(1)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)


class GlImage:
    def __init__(self, file, widget):
        self.file = file
        self.filename = os.path.basename(self.file)
        self.image = Image.open(file)

        self.theta = [0, 0, 0]
        self.position = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.widget = widget

        self.vertices, self.indices = image_gl(self.image, self.widget.grid_maxes)

        self.vao, self.vbo, self.ebo = None, None, None

        self.transformation_matrix = None
        self.set_transformation_matrix()

        self.visible = True

    def gl_calls(self):
        self.vao, self.vbo, self.ebo = create_vao([self.vertices, self.indices])

    def set_transformation_matrix(self):
        self.transformation_matrix = position_matrix(self.theta, self.position, self.scale, reverse=True) \
                                     @ position_matrix(self.widget.theta, [0., 0., 0.], [1., 1., 1.])

    def draw(self):
        self.set_transformation_matrix()

        if not self.visible:
            return

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBindVertexArray(self.vao)
        glUniformMatrix4fv(self.widget.model_loc, 1, GL_FALSE, self.transformation_matrix)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)


class GlGrid:
    def __init__(self, widget, maxes=None):
        self.widget = widget

        if maxes:
            self.maxes = maxes
        else:
            self.maxes = np.sum([model.maxes for model in self.widget.models], axis=0)

        self.grid_vertices, self.grid_indices, self.widget.grid_maxes = grid_gl(*self.maxes)
        self.grid_maxes = self.widget.grid_maxes
        self.vao, self.vbo, self.ebo = None, None, None

    def gl_calls(self):
        self.vao, self.vbo, self.ebo = create_vao([self.grid_vertices, self.grid_indices])

    def draw(self):
        transformation_matrix = position_matrix(self.widget.theta,
                                                [0., 0., 0.],
                                                [1., 1., 1.])

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBindVertexArray(self.vao)
        glUniformMatrix4fv(self.widget.model_loc, 1, GL_FALSE, transformation_matrix)
        glLineWidth(2)
        glDrawElements(GL_LINES, len(self.grid_indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
