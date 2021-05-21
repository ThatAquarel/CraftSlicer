import numpy as np
import pyrr
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from gl_shaders import vertex_shader, fragment_shader
from render import vector_to_vertex_index


# noinspection DuplicatedCode
def vertex_index_to_gl(face_vertices, indices):
    indices = np.array(indices, dtype=int)
    face_vertices = np.array(face_vertices, dtype=np.float32)[indices]

    face_vertices = np.reshape(face_vertices, (-1, 3))

    x_min, y_min, z_min = np.amin(face_vertices, axis=0)
    face_vertices[:, 0] -= x_min
    face_vertices[:, 1] -= y_min
    face_vertices[:, 2] -= z_min
    vertices = face_vertices

    face_colors = np.repeat([[0.7, 0.7, 0.7]], face_vertices.shape[0], axis=0)
    line_colors = np.repeat([[1.0, 1.0, 1.0]], face_vertices.shape[0], axis=0)

    line_vertices = np.concatenate((face_vertices, line_colors), axis=1)
    line_vertices = np.reshape(line_vertices, (-1, 3, 6))
    q, _ = divmod(line_vertices.shape[0], 10000)
    line_vertices = line_vertices[0::q + 1]
    line_vertices = line_vertices.reshape((-1, 6))
    face_vertices = np.concatenate((face_vertices, face_colors), axis=1)

    x_max, y_max, z_max = np.amax(vertices, axis=0)
    for vertices_ in [face_vertices, line_vertices]:
        for column, max_ in zip([0, 1, 2], [x_max, y_max, z_max]):
            vertices_[:, column] -= max_ / 2

    face_vertices, indices = face_vertices.flatten(), indices.flatten()

    return face_vertices.astype(np.float32), line_vertices.flatten().astype(np.float32), vertices, indices.astype(
        np.uint32)


# noinspection DuplicatedCode
def grid_gl(x_max, y_max, z_max):
    xy_max = max([x_max, y_max])
    xy_max = int(xy_max / np.sin(np.pi / 4))
    q, r = divmod(xy_max, 10)
    xy_max = (q + 1) * 10

    grid_x = np.array([[[i, 0, 0], [i, xy_max, 0]] for i in range(0, xy_max + 10, 10)])
    grid_y = np.array([[[0, i, 0], [xy_max, i, 0]] for i in range(0, xy_max + 10, 10)])
    grid_z = np.array([[[0, 0, 0], [0, 0, z_max]]])
    grid_vertices, grid_indices = vector_to_vertex_index(np.concatenate((grid_x, grid_y, grid_z)), dimensions=2)
    grid_indices = np.array(grid_indices, dtype=int)
    grid_vertices = np.array(grid_vertices, dtype=np.float32)[grid_indices]
    grid_vertices = np.reshape(grid_vertices, (-1, 3))

    grid_color_values = np.repeat([[1.0, 1.0, 1.0]], grid_vertices.shape[0], axis=0)
    grid_color_values[0] = [0.0, 1.0, 0.0]
    grid_color_values[1] = [0.0, 1.0, 0.0]
    grid_color_values[grid_x.reshape((-1, 3)).shape[0]] = [1.0, 0.0, 0.0]
    grid_color_values[grid_x.reshape((-1, 3)).shape[0] + 1] = [1.0, 0.0, 0.0]
    grid_color_values[grid_color_values.shape[0] - 1] = [0.0, 0.0, 1.0]
    grid_color_values[grid_color_values.shape[0] - 2] = [0.0, 0.0, 1.0]

    for column, max_ in zip([0, 1, 2], [xy_max, xy_max, z_max]):
        grid_vertices[:, column] -= max_ / 2

    grid_vertices = np.concatenate((grid_vertices, grid_color_values), axis=1)
    grid_vertices, grid_indices = grid_vertices.astype(np.float32), grid_indices.astype(np.uint32)

    return grid_vertices.flatten(), grid_indices.flatten()


# noinspection DuplicatedCode
def write_vao(vao_id, vbo_id, ebo_id, vertices, indices):
    glBindVertexArray(vao_id)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_id)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_id)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 6, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 6, ctypes.c_void_p(12))

    glBindVertexArray(0)


def create_vao(*args):
    vao = glGenVertexArrays(len(args))
    vbo = glGenBuffers(len(args))
    ebo = glGenBuffers(len(args))

    if len(args) == 1:
        write_vao(vao, vbo, ebo, *args[0])
    else:
        for i, (vertices, indices) in enumerate(args):
            write_vao(vao[i], vbo[i], ebo[i], vertices, indices)

    return vao, vbo, ebo


def compile_shader(vertex_src, fragment_src):
    return compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                          compileShader(fragment_src, GL_FRAGMENT_SHADER))


# noinspection DuplicatedCode
def display_setup(x_max, y_max, _):
    shader = compile_shader(vertex_shader, fragment_shader)
    glUseProgram(shader)

    glClearColor(80 / 255, 91 / 255, 103 / 255, 1)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, x_max * 2)

    view = pyrr.matrix44.create_look_at(pyrr.Vector3([y_max * -6, 0, 0]),
                                        pyrr.Vector3([0, 0, 0]),
                                        pyrr.Vector3([0, 1, 0]))

    model_loc = glGetUniformLocation(shader, "model")
    proj_loc = glGetUniformLocation(shader, "projection")
    view_loc = glGetUniformLocation(shader, "view")

    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    return model_loc, proj_loc, view_loc


def position_matrix(theta_x, theta_y, theta_z, pos_x, pos_y, pos_z):
    pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([pos_x, pos_y, pos_z]))
    rot_x = pyrr.Matrix44.from_x_rotation(theta_x)
    rot_y = pyrr.Matrix44.from_y_rotation(theta_y)
    rot_z = pyrr.Matrix44.from_z_rotation(theta_z)

    return rot_x @ rot_y @ rot_z @ pos
