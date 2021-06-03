import stl
from tests.render import vector_to_vertex_index

mesh = stl.mesh.Mesh.from_file("..\\models\\TestHouse.stl")

assert len(mesh.vectors) > 3, "Not readable stl"
vertices_, faces_ = vector_to_vertex_index(mesh.vectors)

print(vertices_)
print(faces_)
