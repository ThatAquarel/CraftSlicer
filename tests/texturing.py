import matplotlib.pyplot as plt
import numpy as np

voxels = np.ones((2, 2, 2), dtype=int)
colors = np.zeros((2, 2, 2, 3), dtype=float)
# colors[0, 0, 0] = 1

image = np.array([
    [[255, 0, 0], [0, 255, 0]],
    [[0, 0, 255], [0, 255, 0]],
    [[0, 0, 255], [0, 255, 0]]
])

# noinspection DuplicatedCode
for i in np.ndindex(image.shape[:2]):
    for k in range(3):
        # transforms

        index = i[0], i[1], k
        bounds = True
        _ = [bounds := bounds & (x < y) for x, y in zip(index, voxels.shape) if bounds]
        if not bounds:
            continue

        if voxels[index] == 1:
            colors[index] = image[i]
            break
colors /= 255

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.voxels(voxels, facecolors=colors)

lim = np.amax(voxels.shape)
ax.set_xlim(0, lim)
ax.set_ylim(0, lim)
ax.set_zlim(0, lim)
ax.set_box_aspect((1, 1, 1))

plt.show()
