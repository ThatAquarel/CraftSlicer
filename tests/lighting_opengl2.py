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
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec3 a_color;
uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
out vec3 v_color;
void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);

    v_color = a_color;
}
"""

fragment_src = """
# version 330
in vec3 v_color;

out vec4 FragColor;
void main()
{    
    //float ambientStrength = 1.1;
    //float ambientStrength = 0.5;
    //vec3 ambient = ambientStrength * vec3(1,0,0);

    //vec3 result = ambient * v_color;
    //FragColor = vec4(result, 1.0);
    FragColor = vec4(v_color, 1.0);
    //FragColor = vec4(1, 0, 0, 1)
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
z_values = cube_vertices[:, 2]
z_max = np.amax(z_values)
z_values = np.reshape(z_values, (-1, 1))
color_values = np.repeat([[0.0, 0.0]], cube_vertices.shape[0], axis=0)
color_values = np.hstack((z_values / z_max, color_values))
# color_values = np.repeat([[1.0, 0.0, 0.0]], cube_vertices.shape[0], axis=0)
cube_vertices = np.concatenate((cube_vertices, color_values), axis=1)

cube_vertices, cube_indices = cube_vertices.flatten(), cube_indices.flatten()
cube_vertices, cube_indices = cube_vertices.astype(np.float32), cube_indices.astype(np.uint32)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
# shader = compileProgram(compileShader(fragment_src, GL_FRAGMENT_SHADER))
# shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER))

# Cube VAO
cube_VAO = glGenVertexArrays(1)
glBindVertexArray(cube_VAO)

# Cube Vertex Buffer Object
cube_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, cube_VBO)
glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)

# Cube Element Buffer Object
cube_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, cube_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, cube_indices.nbytes, cube_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
# glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 3, ctypes.c_void_p(0))
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 6, ctypes.c_void_p(0))

# glEnableVertexAttribArray(2)
glEnableVertexAttribArray(2)
# glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 3, ctypes.c_void_p(12))
# glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 6, ctypes.c_void_p(12))
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 6, ctypes.c_void_p(12))
# glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 6, ctypes.c_void_p(12))

glBindVertexArray(0)

glUseProgram(shader)
# glClearColor(0, 0.1, 0.1, 1)
glClearColor(1, 1, 1, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 10000)
cube_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, -150, 0]))

# eye, target, up
view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 0, 200]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")
switcher_loc = glGetUniformLocation(shader, "switcher")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

# the main application loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUniform1i(switcher_loc, 0)

    rot_x = pyrr.Matrix44.from_x_rotation(np.pi / 2)
    rot_y = pyrr.Matrix44.from_y_rotation(0.5 * glfw.get_time())
    rot_z = pyrr.Matrix44.from_z_rotation(0)

    transformation_matrix = rot_x @ rot_y @ rot_z @ cube_pos

    glBindVertexArray(cube_VAO)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, transformation_matrix)
    glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
    glBindVertexArray(0)

    glfw.swap_buffers(window)
glfw.terminate()
