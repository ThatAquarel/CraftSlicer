import numpy as np
import stl

mesh_1 = stl.mesh.Mesh.from_file("..\\models\\empire.stl")
mesh_2 = stl.mesh.Mesh.from_file("..\\models\\TestHouse.stl")

v_1 = np.unique(
    np.reshape(mesh_1.vectors, (mesh_1.vectors.shape[0] * mesh_1.vectors.shape[1], mesh_1.vectors.shape[2])), axis=1)
v_2 = np.unique(
    np.reshape(mesh_2.vectors, (mesh_2.vectors.shape[0] * mesh_2.vectors.shape[1], mesh_2.vectors.shape[2])), axis=1)

vertices = []
faces = []
for i, triangle in enumerate(mesh_2.vectors):
    j = i * 3
    faces.append([j, j + 1, j + 2])
    for vertex in triangle:
        vertices.append(vertex)
vertices = np.array(vertices)
faces = np.array(faces)

# assert len(mesh.vectors) > 3, "Not readable stl"
# vertices_, faces_ = obj_mesh(mesh.vectors)
#
# print(vertices_)
# print(faces_)
