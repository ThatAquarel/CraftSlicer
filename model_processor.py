import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
from trimesh import remesh

from gl_elements import GlModel, GlGrid, GlVoxel, GlImage
from gl_processor import position_matrix
from tqdm import tqdm


def convert_voxels(models: list[GlModel], grid: GlGrid):
    maxes = np.array(grid.grid_maxes)
    voxels = np.zeros((maxes + 1).astype(int), dtype=int)

    for model in models:
        vertices = np.array(model.face_vertices).reshape((-1, 7))
        transformation_matrix = position_matrix(model.theta, model.position, model.scale, reverse=True)

        vertices = np.delete(vertices, [3, 4, 5], axis=1)
        vertices = vertices @ transformation_matrix
        vertices = np.delete(vertices, 3, axis=1)

        vertices = np.add(vertices, maxes / 2)
        faces = np.array(model.indices).reshape((-1, 3))

        vertices, faces = remesh.subdivide_to_size(vertices=vertices, faces=faces, max_edge=1., max_iter=32)

        indices = np.unique(vertices.astype(int), axis=0).reshape((-1, 3))
        voxels[indices[:, 0], indices[:, 1], indices[:, 2]] = 1

    return voxels


# noinspection DuplicatedCode
def texture_voxels(voxels: list[GlVoxel], images: list[GlImage]):
    voxel_color = np.zeros((*voxels[0].voxels.shape, 3), dtype=int)

    for image in images:
        pixels = np.array(image.image)
        if pixels.shape[-1] == 4:
            pixels = np.delete(pixels, 3, axis=2)

        for i in tqdm(np.ndindex(image.size), total=np.prod(image.size)):
            for k in range(200):
                maxes_skew = np.array([*np.array(image.maxes) / 2, 0]).astype(int)
                pos_skew = np.array([*image.position, 0]).astype(int)

                index = np.array([k, i[0], i[1], 0])
                index -= maxes_skew
                index += pos_skew
                index = np.array(index @ position_matrix(image.theta, image.position, image.scale, reverse=True))
                index = index + maxes_skew
                index = np.array(index).astype(int)
                index = np.delete(index, 3)
                index = tuple(index)

                bounds = True
                _ = [bounds := bounds & (0 < x < y) for x, y in zip(index, voxels[0].voxels.shape) if bounds]
                if not bounds:
                    continue

                if voxels[0].voxels[index] == 1:
                    try:
                        voxel_color[index] = pixels[i[1], i[0]]
                    except IndexError:
                        print("index")
                        pass
                    break

    np.save(".\\tests\\voxel_color.npy", voxel_color)
    np.save(".\\tests\\voxels.npy", voxels[0].voxels)


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

# if __name__ == '__main__':
#     # from models import cube
#     #
#     # matplotlib_show_model(np.array(cube[0]), np.array(cube[1]), [1, 1, 1])
#     voxels_ = np.ones((2, 2, 2), dtype=float)
#     voxels_[0][0][0] = 0
#     from gl_processor import voxel_gl
#
#     vertices_, indices_ = voxel_gl(voxels_)
#     matplotlib_show_model(vertices_, indices_, [2, 2, 2])
