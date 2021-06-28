import math
import time

import numpy as np
from nbt.nbt import NBTFile, \
    TAG_Compound, \
    TAG_Long_Array, \
    TAG_List, \
    TAG_Int, \
    TAG_Long, \
    TAG_String, \
    TAG_BYTE, \
    TAG_COMPOUND
from trimesh import remesh

from core.gl.gl_elements import GlModel, GlGrid, GlVoxel, GlImage
from core.gl.gl_processor import position_matrix


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
        indices = np.clip(indices, [0, 0, 0], maxes.astype(int))
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

    voxels[0].voxel_color = voxel_color
    # np.save(full_path(__file__, "../tests/voxel_color.npy"), voxel_color)
    # np.save(full_path(__file__, "../tests/voxels.npy"), voxels[0].voxels)


def assign_blocks(voxels: np.ndarray, voxel_color: np.ndarray, palette: dict):
    voxels = np.repeat(np.expand_dims(voxels, axis=3), 3, axis=3)

    voxel_color = np.where(voxel_color == [0, 0, 0], [126, 126, 126], voxel_color)
    voxel_color *= voxels
    voxel_color = np.reshape(voxel_color, (-1, 3), "F")
    voxel_color_shape = voxel_color.shape

    colors = np.array(list(palette.values()))
    colors_shape = colors.shape
    colors = np.tile(colors, (voxel_color.shape[0], 1))
    voxel_color = np.repeat(voxel_color, colors_shape[0], axis=0)

    colors_diff = np.absolute(voxel_color - colors)
    colors_diff = colors_diff.reshape((voxel_color_shape[0], colors_shape[0], 3))
    colors_diff = np.sum(colors_diff, axis=2)

    flattened_blocks = np.argmin(colors_diff, axis=1)
    block_types = np.array(list(palette.keys()), dtype=str)
    flattened_blocks = block_types[flattened_blocks]

    return flattened_blocks


def deploy_blocks(voxels: np.ndarray, flattened_blocks: np.ndarray, filename: str):
    block_state_palette, block_states = np.unique(flattened_blocks, return_inverse=True)

    bit_pack_length = len(np.binary_repr(np.int64(len(block_state_palette) - 1)))
    bit_array_length = math.ceil(block_states.shape[0] * bit_pack_length / 64) * 64

    bit_array = np.zeros(bit_array_length, dtype=bool)
    bit_block_states = block_states[:, None] & (1 << np.arange(bit_pack_length)) > 0
    bit_block_states = bit_block_states.flatten()
    bit_indices = np.arange(0, block_states.shape[0] * bit_pack_length)

    bit_array[bit_indices] = bit_block_states

    bit_array = bit_array.astype(int)
    block_states_long_array = np.packbits(bit_array.reshape((-1, 8, 8))[:, :, ::-1]).view(np.int64)

    nbt_structure = {
        "Metadata": {"class": TAG_Compound, "tags": {
            "EnclosingSize": {"class": TAG_Compound, "tags": {
                "x": {"class": TAG_Int, "value": voxels.shape[0]},
                "y": {"class": TAG_Int, "value": voxels.shape[2]},
                "z": {"class": TAG_Int, "value": voxels.shape[1]}
            }},
            "Author": {"class": TAG_String, "value": "Aqua_rel"},
            "Description": {"class": TAG_String, "value": ""},
            "Name": {"class": TAG_String, "value": "CraftSlicer"},
            "RegionCount": {"class": TAG_Int, "value": 1},
            "TimeCreated": {"class": TAG_Long, "value": int(time.time())},
            "TimeModified": {"class": TAG_Long, "value": int(time.time())},
            "TotalBlocks": {"class": TAG_Int, "value": int(np.unique(voxels, return_counts=True)[1][1])},
            "TotalVolume": {"class": TAG_Int, "value": int(np.prod(voxels.shape))}
        }},
        "Regions": {"class": TAG_Compound, "tags": {
            "Region": {"class": TAG_Compound, "tags": {
                "Position": {"class": TAG_Compound, "tags": {
                    "x": {"class": TAG_Int, "value": 0},
                    "y": {"class": TAG_Int, "value": 0},
                    "z": {"class": TAG_Int, "value": 0}
                }},
                "Size": {"class": TAG_Compound, "tags": {
                    "x": {"class": TAG_Int, "value": voxels.shape[0]},
                    "y": {"class": TAG_Int, "value": voxels.shape[2]},
                    "z": {"class": TAG_Int, "value": voxels.shape[1]}
                }},
                "BlockStatePalette": {"class": TAG_List, "tagID": TAG_COMPOUND, "tags": {
                    "".join(" " for _ in range(i)):
                        {"class": TAG_Compound, "tags": {
                            "Name": {"class": TAG_String, "value": block_state}
                        }}
                    for i, block_state in enumerate(block_state_palette)
                }},
                "Entities": {"class": TAG_List, "tagID": TAG_BYTE, "tags": {}},
                "PendingBlockTicks": {"class": TAG_List, "tagID": TAG_BYTE, "tags": {}},
                "PendingFluidTicks": {"class": TAG_List, "tagID": TAG_BYTE, "tags": {}},
                "TileEntities": {"class": TAG_List, "tagID": TAG_BYTE, "tags": {}},
                "BlockStates": {"class": TAG_Long_Array, "value": block_states_long_array}
                # "BlockStates": {"class": TAG_Long_Array, "value": None}
            }}
        }},
        "MinecraftDataVersion": {"class": TAG_Int, "value": 2586},
        "Version": {"class": TAG_Int, "value": 5}
    }

    nbt_file = NBTFile()
    nbt_file.name = filename

    def handle_recursive(parent, items: dict):
        for key, value in items.items():
            tag = value["class"]()

            if " " in key:
                tag.name = ""
            else:
                tag.name = key

            if "tagID" in value:
                tag.tagID = value["tagID"]

            if "tags" in value:
                handle_recursive(tag, value["tags"])
            elif "value" in value:
                tag.value = value["value"]
            parent.tags.append(tag)

    handle_recursive(nbt_file, nbt_structure)

    nbt_file.write_file("%s.litematic" % filename)


if __name__ == '__main__':
    voxels_ = np.load("../tests/voxels.npy")
    # colors_ = np.load("../tests/voxel_color.npy")
    # from core.mc.one_dot_sixteen.one_dot_sixteen import palette as palette_

    # flattened_blocks_ = assign_blocks(voxels_, colors_, palette_)
    # np.save("../tests/flattened_blocks_.npy", flattened_blocks_)

    flattened_blocks_ = np.load("../tests/flattened_blocks_.npy")
    deploy_blocks(voxels_, flattened_blocks_, "test")

    from tests import java_socket

    java_socket.send()
