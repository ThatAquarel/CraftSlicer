import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.collections import PolyCollection

image = np.array(Image.open("..\\models\\empire_jpg.jpg"))
# image = np.array(Image.open("..\\models\\empire.png"))
shape = image.shape

vertices = np.array([
    [[[x, y], [x, y + 1], [x + 1, y]],
     [[x, y], [x, y + 1], [x + 1, y]]]
    for y in range(shape[1]) for x in range(shape[0])
]).reshape((-1, 3, 2))

image_colors = image.copy().astype(np.float32) / 255
colors = np.array([
    [image_colors[x][y], image_colors[x][y]]
    for y in range(shape[1]) for x in range(shape[0])
]).reshape((-1, image.shape[-1]))

fig, ax = plt.subplots()
ax.set(xlim=[0, shape[0]])
ax.set(ylim=[0, shape[1]])
ax.set_aspect("equal")

collection = PolyCollection(vertices, closed=True, facecolors=colors)

ax.add_collection(collection)
plt.show()
