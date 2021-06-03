import numpy as np
import pygame
import stl
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from tests.render import vector_to_vertex_index

stl_model = stl.mesh.Mesh.from_file("..\\models\\TestTorus.stl")

vertices, faces = vector_to_vertex_index(stl_model.vectors)
vertices, faces = np.array(vertices), np.array(faces)

# from models import cube
#
# vertices, faces = cube
# vertices, faces = np.array(vertices) * 10, np.array(faces)

# scene_box = (scene.vertices[0], scene.vertices[0])
# for vertex in scene.vertices:
#     min_v = [min(scene_box[0][i], vertex[i]) for i in range(3)]
#     max_v = [max(scene_box[1][i], vertex[i]) for i in range(3)]
#     scene_box = (min_v, max_v)

# scene_size = [scene_box[1][i] - scene_box[0][i] for i in range(3)]
# max_scene_size = max(scene_size)
# scaled_size = 5
# scene_scale = [scaled_size / max_scene_size for i in range(3)]
# scene_trans = [-(scene_box[1][i] + scene_box[0][i]) / 2 for i in range(3)]
triangles = vertices[faces]


def Model():
    glPushMatrix()
    glScalef(0.1, 0.1, 0.1)
    # glTranslatef(*scene_trans)

    # for mesh in scene.mesh_list:
    #     glBegin(GL_TRIANGLES)
    #     for face in mesh.faces:
    #         for vertex_i in face:
    #             glVertex3f(*scene.vertices[vertex_i])
    #     glEnd()

    glBegin(GL_TRIANGLES)
    for triangle in triangles:
        for vertex_i in triangle:
            glVertex3f(*vertex_i)
    glEnd()

    glPopMatrix()


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 1, 500.0)
    glTranslatef(0.0, 0.0, -10)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    glTranslatef(-0.5, 0, 0)
                if event.key == pygame.K_RIGHT:
                    glTranslatef(0.5, 0, 0)
                if event.key == pygame.K_UP:
                    glTranslatef(0, 1, 0)
                if event.key == pygame.K_DOWN:
                    glTranslatef(0, -1, 0)

        # glRotatef(1, 1, 1, 1)
        glRotatef(0.2, 0.2, 0.2, 0.2)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        Model()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        pygame.display.flip()
        pygame.time.wait(1)


main()
