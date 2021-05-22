from gl_processor import *


class GlModel:
    def __init__(self, vectors, widget):
        self.theta = [0, 0, 0]
        self.position = [0, 0, 0]
        self.widget = widget

        face_vertices, face_indices = vector_to_vertex_index(vectors)
        self.face_vertices, self.line_vertices, self.vertices, self.indices = vertex_index_gl(face_vertices,
                                                                                              face_indices)
        self.maxes = np.amax(self.vertices, axis=0)

        self.vao, self.vbo, self.ebo = create_vao(
            [self.face_vertices, self.indices],
            [self.line_vertices, self.indices])

    def draw(self):
        transformation_matrix = position_matrix(self.widget.theta[0] + self.theta[0],
                                                self.widget.theta[1] + self.theta[1],
                                                self.widget.theta[2] + self.theta[2],
                                                *self.position)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBindVertexArray(self.vao[0])
        glUniformMatrix4fv(self.widget.model_loc, 1, GL_FALSE, transformation_matrix)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBindVertexArray(self.vao[1])
        glUniformMatrix4fv(self.widget.model_loc, 1, GL_FALSE, transformation_matrix)
        glLineWidth(1)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)


class GlImage:
    def __init__(self, image, widget):
        self.theta = [0, 0, 0]
        self.position = [0, 0, 0]
        self.widget = widget


class GlGrid:
    def __init__(self, models, widget):
        self.widget = widget

        self.maxes = np.amax(np.array([model.maxes for model in models]), axis=0)

        self.grid_vertices, self.grid_indices = grid_gl(*self.maxes)
        self.vao, self.vbo, self.ebo = create_vao([self.grid_vertices, self.grid_indices])

    def draw(self):
        transformation_matrix = position_matrix(self.widget.theta[0],
                                                self.widget.theta[1],
                                                self.widget.theta[2],
                                                0, 0, 0)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBindVertexArray(self.vao)
        glUniformMatrix4fv(self.widget.model_loc, 1, GL_FALSE, transformation_matrix)
        glLineWidth(2)
        glDrawElements(GL_LINES, len(self.grid_indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
