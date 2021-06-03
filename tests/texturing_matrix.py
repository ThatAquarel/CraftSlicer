import numpy as np
from core.gl.gl_processor import position_matrix

position_matrix_90 = np.load("position_matrix_90.npy")
position_matrix_0 = position_matrix([0, 0, 0], [0, 0, 0], [1, 1, 1], reverse=True)
print("")
