import numpy as np
from PIL import Image

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
vn 0.000000 0.000000 1.000000

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
    vertices = np.load("vertices.npy")
    vertices, vertex_color = vertices[:, [0, 2, 1]], vertices[:, [3, 4, 5]]
    vertex_indices = np.arange(vertices.shape[0]).reshape((-1, 3)) + 1

    obj_file = open("vertices.obj", "w+")

    obj_file.write("mtllib ./vertices.mtl\n")

    for vertex in vertices:
        obj_file.write("v %.6f %.6f %.6f\n" % tuple(vertex))

    u, v, color_indices = create_uv_map(vertex_color)
    for uv in np.concatenate((u[:, None], v[:, None]), axis=1):
        obj_file.write("vt %.6f %.6f\n" % tuple(uv))

    obj_file.write(obj_content)

    vertex_normals = np.repeat([1, 2, 1, 2, 3, 4, 5, 6, 3, 7, 5, 6], 3)
    vertex_normals = np.tile(vertex_normals, reps=vertex_indices.shape[0] // 12).reshape((-1, 3))
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
    palette_indices = np.arange(0, palette.shape[0])
    palette_x, palette_y = np.divmod(palette_indices, 1024)

    texture_map = np.zeros((1024, 1024, 3), dtype=np.uint8)
    texture_map[palette_x, palette_y] = palette
    image = Image.fromarray(texture_map)
    image.save("vertices.png")

    return palette_y.astype(float) / 1024, 1 - palette_x.astype(float) / 1024, color_indices


if __name__ == '__main__':
    main()
