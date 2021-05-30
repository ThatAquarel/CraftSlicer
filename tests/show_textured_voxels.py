import matplotlib.pyplot as plt
import numpy as np

voxels = np.load("voxels.npy")
colors = np.load("voxel_color.npy")
colors = colors.astype(float)
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
