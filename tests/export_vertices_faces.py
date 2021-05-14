import stl
from render import obj_mesh

mesh = stl.mesh.Mesh.from_file("..\\models\\TestHouse.stl")

assert len(mesh.vectors) > 3, "Not readable stl"
vertices_, faces_ = obj_mesh(mesh.vectors)

print(vertices_)
print(faces_)
