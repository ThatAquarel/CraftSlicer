import glfw
import numpy as np
import pyrr
import stl
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from render import obj_mesh

vertex_src = """
# version 330
layout(location = 0) in vec3 a_position;
//layout(location = 1) in vec2 a_texture;
//layout(location = 2) in vec3 a_color;
layout(location = 1) in vec3 a_color;
uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
out vec3 v_color;
//out vec2 v_texture;
void main()
{
    //gl_Position = projection * view * model * gl_Vertex;
    gl_Position = projection * view * model * vec4(a_position, 1.0);
    //v_texture = a_texture;
    v_color = a_color;
}
"""

fragment_src = """
# version 330
//in vec2 v_texture;
in vec3 v_color;
out vec4 out_color;
uniform int switcher;
uniform sampler2D s_texture;
void main()
{
    //if (switcher == 0){
    //    out_color = texture(s_texture, v_texture);
    //}
    //else if (switcher == 1){
    //    out_color = vec4(v_color, 1.0);   
    //}
    out_color = vec4(v_color, 1.0);
}
"""


# glfw callback functions
def window_resize(_, width, height):
    glViewport(0, 0, width, height)
    projection_ = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 10000)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection_)


# initializing glfw library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# creating the window
window = glfw.create_window(1280, 720, "My OpenGL window", None, None)

# check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# set window's position
glfw.set_window_pos(window, 400, 200)

# set the callback function for window resize
glfw.set_window_size_callback(window, window_resize)

# make the context current
glfw.make_context_current(window)

model_mesh = stl.mesh.Mesh.from_file("..\\models\\statue.stl")
cube_vertices, cube_indices = obj_mesh(model_mesh.vectors)

cube_indices = np.array(cube_indices, dtype=int)
cube_vertices = np.array(cube_vertices, dtype=np.float32)[cube_indices]

cube_vertices = np.reshape(cube_vertices, (-1, 3))
# z_values = cube_vertices[:, 2]
# z_max = np.amax(z_values)
# z_values = np.reshape(z_values, (-1, 1))
# color_values = np.repeat([[0.0, 0.0]], cube_vertices.shape[0], axis=0)
# color_values = np.hstack((z_values / z_max, color_values))

x_min, y_min, z_min = np.amin(cube_vertices, axis=0)
cube_vertices[:, 0] -= x_min
cube_vertices[:, 1] -= y_min
cube_vertices[:, 2] -= z_min
x_max, y_max, z_max = np.amax(cube_vertices, axis=0)

color_values = np.repeat([[0.7, 0.7, 0.7]], cube_vertices.shape[0], axis=0)
color_values_ = np.repeat([[1.0, 1.0, 1.0]], cube_vertices.shape[0], axis=0)

cube_vertices_ = np.concatenate((cube_vertices, color_values_), axis=1)
cube_vertices_ = np.reshape(cube_vertices_, (-1, 3, 6))
q, _ = divmod(cube_vertices_.shape[0], 8192)
cube_vertices_ = cube_vertices_[0::q + 1]
cube_vertices = np.concatenate((cube_vertices, color_values), axis=1)

cube_vertices, cube_indices = cube_vertices.flatten(), cube_indices.flatten()
cube_vertices_ = cube_vertices_.flatten().astype(np.float32)
cube_vertices, cube_indices = cube_vertices.astype(np.float32), cube_indices.astype(np.uint32)


def obj_mesh_line(vectors):
    vertices = [vertex for triangle in vectors for vertex in triangle]

    i = vectors.shape[0] * 2
    faces = list(np.linspace(0, i, i, endpoint=False).reshape((vectors.shape[0], 2)).astype(int))

    return vertices, faces


xy_max = int(max([x_max, y_max]))
q, r = divmod(xy_max, 10)
xy_max = (q + 1) * 10
grid_x = np.array([[[i, 0, 0], [i, xy_max, 0]] for i in range(0, xy_max + 10, 10)])
grid_y = np.array([[[0, i, 0], [xy_max, i, 0]] for i in range(0, xy_max + 10, 10)])
grid_z = np.array([[[0, 0, 0], [0, 0, z_max]]])
grid_vertices, grid_indices = obj_mesh_line(np.concatenate((grid_x, grid_y, grid_z)))
grid_indices = np.array(grid_indices, dtype=int)
grid_vertices = np.array(grid_vertices, dtype=np.float32)[grid_indices]
grid_vertices = np.reshape(grid_vertices, (-1, 3))

grid_color_values = np.repeat([[1.0, 1.0, 1.0]], grid_vertices.shape[0], axis=0)
grid_color_values[0] = [1.0, 0.0, 0.0]
grid_color_values[1] = [1.0, 0.0, 0.0]
grid_color_values[grid_x.reshape((-1, 3)).shape[0]] = [0.0, 1.0, 0.0]
grid_color_values[grid_x.reshape((-1, 3)).shape[0] + 1] = [0.0, 1.0, 0.0]
grid_color_values[grid_color_values.shape[0] - 1] = [0.0, 0.0, 1.0]
grid_color_values[grid_color_values.shape[0] - 2] = [0.0, 0.0, 1.0]

grid_vertices = np.concatenate((grid_vertices, grid_color_values), axis=1)
grid_vertices, grid_indices = grid_vertices.astype(np.float32), grid_indices.astype(np.uint32)
grid_vertices, grid_indices = grid_vertices.flatten(), grid_indices.flatten()

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

# Cube VAO
cube_VAO, line_VAO, grid_VAO = glGenVertexArrays(3)

glBindVertexArray(cube_VAO)
cube_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, cube_VBO)
glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)

cube_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, cube_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, cube_indices.nbytes, cube_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 6, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 6, ctypes.c_void_p(12))

glBindVertexArray(line_VAO)
line_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, line_VBO)
glBufferData(GL_ARRAY_BUFFER, cube_vertices_.nbytes, cube_vertices_, GL_STATIC_DRAW)

line_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, line_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, cube_indices.nbytes, cube_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_vertices_.itemsize * 6, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, cube_vertices_.itemsize * 6, ctypes.c_void_p(12))

glBindVertexArray(grid_VAO)
grid_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, grid_VBO)
glBufferData(GL_ARRAY_BUFFER, grid_vertices.nbytes, grid_vertices, GL_STATIC_DRAW)

grid_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, grid_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, grid_indices.nbytes, grid_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, grid_vertices.itemsize * 6, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, grid_vertices.itemsize * 6, ctypes.c_void_p(12))

glBindVertexArray(0)

glUseProgram(shader)
glClearColor(80 / 255, 91 / 255, 103 / 255, 1)
# glClearColor(1, 1, 1, 1)

glfw.window_hint(glfw.SAMPLES, 8)
# glfwWindowHint(GLFW_SAMPLES, 4)
glEnable(GL_MULTISAMPLE)

glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 10000)
# cube_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([y, z, x]))
cube_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))

# eye, target, up
view = pyrr.matrix44.create_look_at(pyrr.Vector3([y_max * 4, z_max / 2, x_max * 4]),
                                    pyrr.Vector3([y_max / 2, z_max / 2, x_max / 2]),
                                    pyrr.Vector3([0, 1, 0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

# the main application loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    rot_x = pyrr.Matrix44.from_x_rotation(np.pi / 2)
    rot_y = pyrr.Matrix44.from_y_rotation(0.5 * glfw.get_time())
    rot_z = pyrr.Matrix44.from_z_rotation(0)

    transformation_matrix = rot_x @ rot_y @ rot_z @ cube_pos

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glBindVertexArray(grid_VAO)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, transformation_matrix)
    glLineWidth(2)
    glDrawElements(GL_LINES, len(grid_indices), GL_UNSIGNED_INT, None)

    glBindVertexArray(line_VAO)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, transformation_matrix)
    glLineWidth(1)
    glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glBindVertexArray(cube_VAO)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, transformation_matrix)
    glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
    glBindVertexArray(0)

    glfw.swap_buffers(window)
glfw.terminate()
