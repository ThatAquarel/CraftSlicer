import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
from trimesh import remesh

from gl_elements import GlModel, GlGrid


def convert_voxels(models: list[GlModel], grid: GlGrid):
    maxes = np.array(grid.grid_maxes)
    voxels = np.zeros((maxes + 1).astype(int), dtype=int)

    for model in models:
        vertices = np.array(model.face_vertices).reshape((-1, 7))
        vertices = np.delete(vertices, [3, 4, 5, 6], axis=1)
        vertices = np.add(vertices, maxes / 2)
        faces = np.array(model.indices).reshape((-1, 3))

        vertices, faces = remesh.subdivide_to_size(vertices=vertices, faces=faces, max_edge=1., max_iter=32)

        indices = np.unique(vertices.astype(int), axis=0).reshape((-1, 3))
        voxels[indices[:, 0], indices[:, 1], indices[:, 2]] = 1

    return voxels

    # matplotlib_show_voxel(voxels, maxes)


# noinspection PyUnresolvedReferences
def matplotlib_show_model(vertices, faces, maxes):
    vectors = vertices[faces]

    fig = plt.figure()
    ax = mplot3d.Axes3D(fig, auto_add_to_figure=False)
    fig.add_axes(ax)
    collections = mplot3d.art3d.Poly3DCollection(vectors)
    collections.set_facecolor("w")
    collections.set_edgecolor("b")

    ax.add_collection3d(collections)

    lim = np.amax(maxes)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_zlim(0, lim)
    ax.set_box_aspect((1, 1, 1))

    plt.show()


def matplotlib_show_voxel(voxels, maxes):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.voxels(voxels, facecolors="w", edgecolor='b')

    lim = np.amax(maxes)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_zlim(0, lim)
    ax.set_box_aspect((1, 1, 1))

    plt.show()
