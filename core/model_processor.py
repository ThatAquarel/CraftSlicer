import numpy as np
from trimesh import remesh

from core.gl.gl_elements import GlModel, GlGrid, GlVoxel, GlImage
from core.gl.gl_processor import position_matrix
from core.util import full_path


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


def texture_voxels(voxels: list[GlVoxel], images: list[GlImage]):
    voxel_color = np.zeros((*voxels[0].voxels.shape, 3), dtype=int)

    depth = 200
    layer_depth = 1
    for image in images:
        pixels = np.array(image.image)
        if pixels.shape[-1] == 4:
            pixels = np.delete(pixels, 3, axis=2)

        maxes_skew = (np.array([*image.maxes, 0]) / 2).astype(int)
        pos_skew = np.array([*image.position, 0]).astype(int)

        pixel_indices = np.array([i for i in np.ndindex(1, *image.size)])
        pixel_indices = np.flip(pixel_indices, axis=1)
        pixel_indices = np.tile(pixel_indices, (depth, 1))

        voxel_indices = np.array([i for i in np.ndindex(depth, *image.size, 1)])
        voxel_indices += -maxes_skew + pos_skew
        voxel_indices = voxel_indices @ np.array(
            position_matrix(image.theta, image.position, image.scale, reverse=True))
        voxel_indices += maxes_skew
        voxel_indices = voxel_indices.astype(int)
        voxel_indices = np.delete(voxel_indices, 3, axis=1)

        a = 0 <= voxel_indices
        a &= voxel_indices < voxels[0].voxels.shape
        a = a[:, 0] & a[:, 1] & a[:, 2]
        voxel_indices = voxel_indices[a]
        pixel_indices = pixel_indices[a]

        b = voxels[0].voxels[voxel_indices[:, 0], voxel_indices[:, 1], voxel_indices[:, 2]] == 1
        voxel_indices = voxel_indices[b]
        pixel_indices = pixel_indices[b]

        pixel_indices_ = pixel_indices.copy()
        c = np.array([], dtype=int)
        for i in range(layer_depth):
            pixel_indices_[c] = -1
            _, d = np.unique(pixel_indices_, axis=0, return_index=True)
            d = d[1:]
            c = np.append(c, d)
        pixel_indices = pixel_indices[c]
        voxel_indices = voxel_indices[c]

        voxel_color[voxel_indices[:, 0], voxel_indices[:, 1], voxel_indices[:, 2]] = \
            pixels[pixel_indices[:, 0], pixel_indices[:, 1]]

    np.save(full_path(__file__, "../tests/voxel_color.npy"), voxel_color)
    np.save(full_path(__file__, "../tests/voxels.npy"), voxels[0].voxels)
