import numpy as np
import string


def main():
    vertices = np.load("vertices.npy")
    vertices, vertices_color = vertices[:, [0, 2, 1]], vertices[:, [3, 4, 5]]
    indices = np.arange(length := vertices.shape[0]).reshape((-1, 3)) + 1

    obj_file = open("vertices.obj", "w+")

    obj_file.write("mtllib ./vertices.mtl\n")

    for vertex in vertices:
        obj_file.write("v %.6f %.6f %.6f\n" % tuple(vertex))

    obj_file.write("""
    vn 1.000000 0.000000 0.000000
    vn -1.000000 0.000000 0.000000
    vn 0.000000 0.000000 -1.000000
    vn 0.000000 0.000000 1.000000
    vn 0.000000 1.000000 0.000000
    vn 0.000000 -1.000000 0.000000
    vn 0.000000 0.000000 1.000000

    o default
    usemtl vertices
    """)

    vertex_normals = np.repeat([1, 2, 1, 2, 3, 4, 5, 6, 3, 7, 5, 6], 3)
    vertex_normals = np.tile(vertex_normals, reps=indices.shape[0] // 12).reshape((-1, 3))
    faces = np.hstack((indices, vertex_normals))[:, [0, 3, 1, 4, 2, 5]]

    for i, face in enumerate(faces):
        obj_file.write("usemtl %s\nf %i//%i %i//%i %i//%i\n" % tuple(face))
    obj_file.close()

    mtl_file = open("vertices.mtl", "w+")
    mtl_file.write("""
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
    """)

    palette, palette_indices = np.unique(vertices_color, axis=0, return_inverse=True)

    letters = np.array(list(string.ascii_letters))
    palette_identifiers = np.random.randint(0, letters.shape[0],
                                            size=(palette_length := palette.shape[0]) * 32).reshape((-1, 32))
    palette_identifiers = letters[palette_identifiers]
    palette_identifiers = np.array(["".join(i) for i in palette_identifiers])

    color_template = """
    newmtl %s
    Ka 1 1 1
    Kd %0.6f %0.6f %0.6f
    Ks 1 1 1
    Ns 50
    illum 7
    """
    for identifier, color in zip(palette_identifiers, palette):
        mtl_file.write(color_template % (identifier, *color))
    mtl_file.close()


if __name__ == '__main__':
    main()
