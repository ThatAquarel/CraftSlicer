import os

# noinspection PyPackageRequirements
import stl
from PIL import Image

from craftslicer.core.gl.gl_processor import *


class GlElement:
    def __init__(self, widget):
        self.widget = widget

        self.theta = [0, 0, 0]
        self.position = [0, 0, 0]
        self.scale = [1, 1, 1]

        self.face_vertices, self.line_vertices, self.vertices, self.indices = None, None, None, None
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


class GlElementSimple(GlElement):
    def __init__(self, widget):
        super(GlElementSimple, self).__init__(widget)

    def gl_calls(self):
        self.vao, self.vbo, self.ebo = create_vao([self.vertices, self.indices])


class GlModel(GlElement):
    def __init__(self, file, widget):
        super(GlModel, self).__init__(widget)

        self.file = file
        self.filename = os.path.basename(self.file)
        self.model_mesh = stl.mesh.Mesh.from_file(file)

        self.face_vertices, self.line_vertices, self.vertices, self.indices = vector_gl(self.model_mesh.vectors)
        self.maxes = np.amax(self.vertices, axis=0)


class GlVoxel(GlElement):
    def __init__(self, voxel, widget, voxel_color=None):
        super().__init__(widget)

        self.voxels = voxel
        self.voxel_color = voxel_color
        self.flattened_blocks = None

        self.face_vertices, self.line_vertices, self.vertices, self.indices = voxel_gl(voxel,
                                                                                       self.widget.grid_maxes,
                                                                                       voxel_color=voxel_color)


class GlImage(GlElementSimple):
    def __init__(self, file, widget):
        super(GlImage, self).__init__(widget)

        self.file = file
        self.filename = os.path.basename(self.file)
        self.pil_image = Image.open(file)

        self.maxes = [i for i in self.widget.grid_maxes]
        self.vertices, self.indices, self.size, self.image = image_gl(self.pil_image, self.widget.grid_maxes)

    def draw(self):
        self.set_transformation_matrix()

        if not self.visible:
            return

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBindVertexArray(self.vao)
        glUniformMatrix4fv(self.widget.model_loc, 1, GL_FALSE, self.transformation_matrix)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)


class GlGrid(GlElementSimple):
    def __init__(self, widget, maxes=None):
        super().__init__(widget)

        if maxes:
            self.maxes = maxes
        else:
            self.maxes = np.sum([model.maxes for model in self.widget.models], axis=0)

        self.vertices, self.indices, self.widget.grid_maxes = grid_gl(*self.maxes)
        self.grid_maxes = self.widget.grid_maxes

    def draw(self):
        self.set_transformation_matrix()

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBindVertexArray(self.vao)
        glUniformMatrix4fv(self.widget.model_loc, 1, GL_FALSE, self.transformation_matrix)
        glLineWidth(2)
        glDrawElements(GL_LINES, len(self.indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
