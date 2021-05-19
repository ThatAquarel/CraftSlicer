from gl_processor import *


class GlModel:
    def __init__(self, vectors):
        face_vertices, face_indices = vector_to_vertex_index(vectors)

        self.face_vertices, self.line_vertices, self.vertices, self.indices = vertex_index_to_gl(face_vertices,
                                                                                                 face_indices)
        self.vao, self.vbo, self.ebo = create_vao(
            [self.face_vertices, self.indices],
            [self.line_vertices, self.indices])
