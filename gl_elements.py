from gl_processor import *


class GlModel:
    def __init__(self, vectors, widget):
        self.theta = [0, 0, 0]
        self.position = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.widget = widget

        self.face_vertices, self.line_vertices, self.vertices, self.indices = vector_gl(vectors)
        self.maxes = np.amax(self.vertices, axis=0)

        self.vao, self.vbo, self.ebo = None, None, None

        self.transformation_matrix = None
        self.set_transformation_matrix()

    def gl_calls(self):
        self.vao, self.vbo, self.ebo = create_vao(
            [self.face_vertices, self.indices],
            [self.line_vertices, self.indices])

    def set_transformation_matrix(self):
        self.transformation_matrix = position_matrix(
            [theta + theta_ for theta, theta_ in zip(self.widget.theta, self.theta)],
            self.position,
            self.scale)

    def draw(self):
        self.set_transformation_matrix()

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
    def __init__(self, image, widget):
        self.theta = [0, 0, 0]
        self.position = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.widget = widget

        self.vertices, self.indices = image_gl(image, self.widget.visual_offset)

        self.vao, self.vbo, self.ebo = None, None, None

        self.transformation_matrix = None
        self.set_transformation_matrix()

    def gl_calls(self):
        self.vao, self.vbo, self.ebo = create_vao([self.vertices, self.indices])

    def set_transformation_matrix(self):
        self.transformation_matrix = position_matrix(
            [theta + theta_ for theta, theta_ in zip(self.widget.theta, self.theta)],
            self.position,
            self.scale)

    def draw(self):
        self.set_transformation_matrix()

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
            self.maxes = np.amax(np.array([model.maxes for model in self.widget.models]), axis=0)

        self.grid_vertices, self.grid_indices, self.widget.visual_offset = grid_gl(*self.maxes)
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
