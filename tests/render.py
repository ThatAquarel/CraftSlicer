import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection


def vector_to_vertex_index(vectors, dimensions=3):
    vertices = [vertex for triangle in vectors for vertex in triangle]

    i = vectors.shape[0] * dimensions
    faces = list(np.linspace(0, i, i, endpoint=False).reshape((vectors.shape[0], dimensions)).astype(int))

    return vertices, faces


def frustum(left, right, bottom, top, z_near, z_far):
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = +2.0 * z_near / (right - left)
    m[1, 1] = +2.0 * z_near / (top - bottom)
    m[2, 2] = -(z_far + z_near) / (z_far - z_near)
    m[0, 2] = (right + left) / (right - left)
    m[2, 1] = (top + bottom) / (top - bottom)
    m[2, 3] = -2.0 * z_near * z_far / (z_far - z_near)
    m[3, 2] = -1.0
    return m


def perspective(fov_y, aspect, z_near, z_far):
    h = np.tan(0.5 * np.radians(fov_y)) * z_near
    w = h * aspect
    return frustum(-w, w, -h, h, z_near, z_far)


def translate(x, y, z):
    return np.array([[1, 0, 0, x], [0, 1, 0, y],
                     [0, 0, 1, z], [0, 0, 0, 1]], dtype=float)


def x_rotate(theta):
    t = np.pi * theta / 180
    c, s = np.cos(t), np.sin(t)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0],
                     [0, s, c, 0], [0, 0, 0, 1]], dtype=float)


def y_rotate(theta):
    t = np.pi * theta / 180
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0],
                     [-s, 0, c, 0], [0, 0, 0, 1]], dtype=float)


def z_rotate(theta):
    t = np.pi * theta / 180
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0],
                     [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)


class Render:
    def __init__(self, vertices, faces, figure):
        self.theta = [90, 180, 90]
        self.translate = [0, 0, -3.5]

        self.theta_ = [90, 180, 90]
        self.translate_ = [0, 0, -3.5]
        self.mouse_ = [0, 0]
        self.vector_ = [0, 0]

        self.V = np.array(vertices)
        self.F = np.array(faces)
        self.press = False

        self.fig = figure
        self.fig.set(facecolor="slategrey")
        x, y = figure.get_size_inches() * figure.dpi
        x_lim = x / y
        self.ax = self.fig.add_axes([0, 0, 1, 1], xlim=[-x_lim, +x_lim], ylim=[-1, +1], frameon=False)

        render = self.render(self.theta, self.translate)
        self.collection = PolyCollection(render[0], closed=True, facecolor=render[1])

        self.ax.add_collection(self.collection)

    def draw(self, x, y):
        render = self.render(self.theta, self.translate)
        x_lim = x / y
        self.ax.set_xlim(-x_lim, +x_lim)
        self.collection.set(verts=render[0])
        self.collection.set(facecolor=render[1])
        self.fig.model_canvas.draw_idle()

    def on_move(self, event):
        if not self.press or not event.inaxes:
            return

        self.vector_ = [event.xdata - self.mouse_[0], event.ydata - self.mouse_[1]]

        self.theta[0] = self.theta_[0] + (self.vector_[1] * -100)
        self.theta[2] = self.theta_[2] + (self.vector_[0] * 100)

        self.draw(*self.fig.get_size_inches() * self.fig.dpi)

    def on_press(self, event):
        if not event.inaxes or self.press:
            return
        self.press = True
        self.theta_ = [deg for deg in self.theta]
        self.translate_ = [vec for vec in self.translate]

        self.mouse_ = [event.xdata, event.ydata]

    def on_release(self, _):
        self.press = False
        self.theta_ = [deg for deg in self.theta]
        self.translate_ = [vec for vec in self.translate]

        self.mouse_ = [0, 0]
        self.vector_ = [0, 0]

    def render(self, rotate_vector, translate_vector):
        v, f = self.V, self.F

        v = (v - (v.max(0, initial=0) + v.min(0, initial=0)) / 2) / max(v.max(0, initial=0) - v.min(0, initial=0))
        mvp = perspective(25, 1, 1, 100) @ translate(translate_vector[0], translate_vector[1],
                                                     translate_vector[2]) @ x_rotate(
            rotate_vector[0]) @ y_rotate(rotate_vector[1]) @ z_rotate(rotate_vector[2])
        v = np.c_[v, np.ones(len(v))] @ mvp.T
        v /= v[:, 3].reshape(-1, 1)
        v = v[f]
        t = v[:, :, :2]
        z = -v[:, :, 2].mean(axis=1)
        z_min, z_max = z.min(), z.max()
        z = (z - z_min) / (z_max - z_min)
        c = plt.get_cmap("magma")(z)
        i = np.argsort(z)
        # t, c =

        return t[i, :], c[i, :]


if __name__ == '__main__':
    import stl

    mesh = stl.mesh.Mesh.from_file("../models/statue.stl")

    assert len(mesh.vectors) > 3, "Not readable stl"
    vertices_, faces_ = vector_to_vertex_index(mesh.vectors)

    # from models import house
    #
    # vertices_, faces_ = house

    fig = plt.figure(figsize=(8, 8))
    renderer = Render(vertices_, faces_, fig)

    plt.connect('button_press_event', renderer.on_press)
    plt.connect('button_release_event', renderer.on_release)
    plt.connect('motion_notify_event', renderer.on_move)
    plt.show()
