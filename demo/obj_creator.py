import numpy as np
from PIL import Image

directions = np.array([
    [-1, 0, 0],
    [1, 0, 0],
    [0, -1, 0],
    [0, 1, 0],
    [0, 0, -1],
    [0, 0, 1]
])

cube_faces = np.array([
    [0, 2, 3, 0, 1, 3],  # right
    [4, 6, 7, 4, 5, 7],  # left
    [0, 4, 5, 0, 1, 5],  # front
    [2, 6, 7, 2, 3, 7],  # back
    [0, 2, 4, 2, 4, 6],  # bottom
    [1, 3, 5, 3, 5, 7],  # top
])

cube_vertices = np.array([
    [0, 0, 0],  # 0
    [0, 0, 1],  # 1
    [0, 1, 0],  # 2
    [0, 1, 1],  # 3
    [1, 0, 0],  # 4
    [1, 0, 1],  # 5
    [1, 1, 0],  # 6
    [1, 1, 1],  # 7
])

cube_normals = np.array([
    [1, 2],  # right
    [1, 2],  # left
    [3, 4],  # front
    [3, 4],  # back
    [5, 6],  # bottom
    [5, 6],  # top
])

mtl_content = """
newmtl vertices
Ns 0.000000
Ka 1.000000 1.000000 1.000000
Kd 0.600000 0.600000 0.600000
Ks 0.000000 0.000000 0.000000
Ke 0.000000 0.000000 0.000000
Ni 1.450000
d 1.000000
illum 1
map_Kd vertices.png
"""

obj_content = """
vn 1.000000 0.000000 0.000000
vn -1.000000 0.000000 0.000000
vn 0.000000 0.000000 -1.000000
vn 0.000000 0.000000 1.000000
vn 0.000000 1.000000 0.000000
vn 0.000000 -1.000000 0.000000

o default
usemtl vertices
"""


def main():
    write_mtl()
    write_obj()


def write_mtl():
    mtl_file = open("vertices.mtl", "w+")
    mtl_file.write(mtl_content)


def write_obj():
    voxels = np.load("voxels.npy")
    voxel_color = np.load("voxel_color.npy")

    vertices, vertex_color, vertex_normals = create_vertices_vertex_color(voxels, voxel_color)

    vertex_indices = np.arange(vertices.shape[0]).reshape((-1, 3)) + 1

    obj_file = open("vertices.obj", "w+")

    obj_file.write("mtllib ./vertices.mtl\n")

    for vertex in vertices:
        obj_file.write("v %.6f %.6f %.6f\n" % tuple(vertex))

    vertex_color[np.where((vertex_color < (25 / 255)).all(axis=1))[0]] = [164 / 255, 143 / 255, 121 / 255]
    u, v, color_indices = create_uv_map(vertex_color)
    for uv in np.concatenate((u[:, None], v[:, None]), axis=1):
        obj_file.write("vt %.6f %.6f\n" % tuple(uv))

    obj_file.write(obj_content)

    color_indices = color_indices.reshape((-1, 3))
    color_indices += 1

    faces = np.hstack((vertex_indices, color_indices, vertex_normals))[:, [0, 3, 6, 1, 4, 7, 2, 5, 8]]

    for i, face in enumerate(faces):
        obj_file.write("f %i/%i/%i %i/%i/%i %i/%i/%i\n" % tuple(face))
    obj_file.close()


def create_uv_map(vertex_color: np.ndarray):
    palette, color_indices = np.unique(vertex_color, axis=0, return_inverse=True)
    palette *= 255
    palette = palette.astype(int)
    palette_indices = np.arange(0, length := palette.shape[0])

    resolution = 2 ** int(np.ceil(np.log2(np.sqrt(length))))
    palette_x, palette_y = np.divmod(palette_indices, resolution)

    texture_map = np.zeros((resolution, resolution, 3), dtype=np.uint8)
    texture_map[palette_x, palette_y] = palette
    image = Image.fromarray(texture_map)
    image.save("vertices.png")

    return palette_y.astype(float) / resolution, 1 - palette_x.astype(float) / resolution, color_indices


def create_vertices_vertex_color(voxels: np.ndarray, voxel_color: np.ndarray):
    global directions, cube_faces, cube_vertices, cube_normals

    selected_blocks = np.argwhere(voxels == 1)
    selected_blocks_ = selected_blocks.copy()
    selected_colors = voxel_color[selected_blocks[:, 0], selected_blocks[:, 1], selected_blocks[:, 2]]

    selected_blocks = np.repeat(selected_blocks, 6, axis=0)
    directions = np.tile(directions, (selected_blocks.shape[0] // 6, 1))
    selected_blocks += directions

    selected_directions = voxels[selected_blocks[:, 0], selected_blocks[:, 1], selected_blocks[:, 2]].astype(bool)
    selected_directions = np.invert(selected_directions)
    selected_directions = np.argwhere(selected_directions.reshape((-1, 6)))

    voxels_faces_indices = (c := selected_directions.flatten())[1::2]
    voxels_faces_color_indices = c[::2]

    voxels_faces = cube_faces[voxels_faces_indices]
    voxels_faces_color = selected_colors[voxels_faces_color_indices]

    vertices = cube_vertices[voxels_faces].reshape((-1, 3))
    selected_blocks_ = selected_blocks_[voxels_faces_color_indices]
    selected_blocks_ = np.repeat(selected_blocks_, 6, axis=0)
    vertices += selected_blocks_
    vertices = vertices[:, [0, 2, 1]]

    vertex_color = np.repeat(voxels_faces_color, 6, axis=0)
    vertex_color = vertex_color.astype(float) / 255

    vertex_normals = np.repeat(cube_normals[voxels_faces_indices].flatten(), 3).reshape((-1, 3))

    return vertices, vertex_color, vertex_normals


if __name__ == '__main__':
    main()
