import numpy as np
import pywavefront
from PIL import Image

from trimesh import remesh
from craftslicer.core.gl.gl_processor import position_matrix
from craftslicer.core.gl.gl_elements import GlModel
from craftslicer.core.gl.gl_processor import vector_to_vertex_index


def obj_to_gl_model(gl_widget, file: str):
    scene = pywavefront.Wavefront(file, create_materials=True, collect_faces=True, cache=True)

    name, material = list(scene.materials.items())[0]
    if material.vertex_format != "T2F_N3F_V3F":
        return None

    packed_data = np.array(material.vertices).reshape((-1, 8))
    vectors = packed_data[:, 5:8]
    vectors = vectors.reshape((-1, 3, 3))

    uv_map = packed_data[:, 0:2]
    u = uv_map[:, 0]
    v = uv_map[:, 1]

    texture_image = np.array(Image.open(material.texture.path))
    w, h, _ = texture_image.shape
    w, h, = w - 1, h - 1

    x = u * w
    y = v * h

    x, y = np.array([x, y], dtype=int)
    vertex_color = texture_image[:, :, [0, 1, 2]][x, y]

    return GlModel(gl_widget, file=file, vectors=vectors, vertex_color=vertex_color)


def vertex_color_to_voxel_color(voxels: np.ndarray, gl_model: GlModel):
    maxes = np.array(gl_model.widget.grid.grid_maxes)

    transformation_matrix = position_matrix(gl_model.theta, gl_model.position, gl_model.scale, reverse=True)
    vectors = gl_model.vectors.reshape((-1, 3))[:, [0, 1, 2, 0]] @ np.array(transformation_matrix)
    vectors = vectors[:, [0, 1, 2]]
    vectors = np.add(vectors, maxes / 2)

    # vertices, faces = vector_to_vertex_index(vectors.reshape((-1, 3, 3)))
    # vertices, faces, indices = remesh.subdivide_to_size(vertices=vertices,
    #                                                     faces=faces,
    #                                                     max_edge=1.,
    #                                                     max_iter=32,
    #                                                     return_index=True)
    # vectors = vertices[faces]

    vectors = vectors.astype(int)
    vectors = np.clip(vectors, [0, 0, 0], maxes.astype(int))

    voxel_color = np.zeros((*voxels.shape, 3), dtype=int)
    voxel_color[vectors[:, 0], vectors[:, 1], vectors[:, 2]] = gl_model.vertex_color

    return voxel_color


class _GlWidget:
    def __init__(self):
        self.grid = _GlGrid()
        self.theta = [0, 0, 0]
        self.position = [0, 0, 0]
        self.scale = [1, 1, 1]


class _GlGrid:
    def __init__(self):
        self.grid_maxes = [50, 50, 50]


if __name__ == '__main__':
    from craftslicer.core.model_processor import convert_voxels

    # gl_model_ = obj_to_gl_model(_GlWidget(), "C:\\Users\\xia_t\\Videos\\CraftSlicerDemo\\model\\untitled.obj")
    gl_model_ = obj_to_gl_model(_GlWidget(), "C:\\Users\\xia_t\\Desktop\\untitled.obj")
    gl_model_.scale = [20, 20, 20]
    # noinspection PyTypeChecker
    voxels_ = convert_voxels([gl_model_], _GlGrid())
    voxel_color_ = vertex_color_to_voxel_color(voxels=voxels_, gl_model=gl_model_)

    # noinspection PyPackageRequirements
    import matplotlib.pyplot as plt
    import numpy as np

    voxel_color_ = voxel_color_.astype(float)
    voxel_color_ /= 255

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.voxels(voxels_, facecolors=voxel_color_)

    lim = np.amax(voxels_.shape)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_zlim(0, lim)
    ax.set_box_aspect((1, 1, 1))

    plt.show()
