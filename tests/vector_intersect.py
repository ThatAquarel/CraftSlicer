from timeit import Timer

import numpy as np


def intersect_triangle(ray_origin, ray_dir, a, b, c):
    e1 = b - a
    e2 = c - a
    n = np.cross(e1, e2)

    det = -np.dot(ray_dir, n)
    if det >= 1e-6:
        return False
    inv_det = 1.0 / det

    ao = ray_origin - a
    dao = np.cross(ao, ray_dir)

    u = np.dot(e2, dao) * inv_det
    if u < 0.0:
        return False

    v = -np.dot(e1, dao) * inv_det
    if v < 0.0:
        return False
    if ~((u + v) <= 1.0):
        return False

    t = np.dot(ao, n) * inv_det
    return t >= 0.0


def intersect_triangle_array(ray_origin, ray_dir, a, b, c):
    e1 = b - a
    e2 = c - a
    n = np.cross(e1, e2)

    det = -np.array([np.dot(a, b) for a, b in zip(ray_dir, n)])

    inv_det = 1.0 / det

    ao = ray_origin - a
    dao = np.cross(ao, ray_dir)

    u = np.array([np.dot(a, b) for a, b in zip(e2, dao)]) * inv_det
    v = -np.array([np.dot(a, b) for a, b in zip(e1, dao)]) * inv_det
    t = np.array([np.dot(a, b) for a, b in zip(ao, n)]) * inv_det

    result = det < 1e-6
    result &= u > 0.0
    result &= v > 0.0
    result &= (u + v) <= 1.0
    return result & (t >= 0.0)


def main():
    i = int(1e+6)

    ray_origin = np.repeat([[0, 0, 0]], i, axis=0)
    ray_dir = np.repeat([[1, -1, 1]], i, axis=0)
    a = np.repeat([[1, 0, 0]], i, axis=0)
    b = np.repeat([[0, 1, 0]], i, axis=0)
    c = np.repeat([[0, 0, 1]], i, axis=0)

    intersect_triangle_array(ray_origin, ray_dir, a, b, c)

    # print(intersect_triangle(np.array([0, 0, 0]),
    #                          np.array([1, 1, 1]),
    #                          np.array([5, 0, 0]),
    #                          np.array([0, 5, 0]),
    #                          np.array([0, 0, 5])))

    # intersect_triangle(np.array([0, 0, 0]),
    #                    np.array([1, -1, 1]),
    #                    np.array([5, 0, 0]),
    #                    np.array([0, 5, 0]),
    #                    np.array([0, 0, 5]))


if __name__ == '__main__':
    timer = Timer(lambda: main())
    print(timer.timeit(number=1))

# ver1 68.7164812 seconds for 1 000 000 iterations
# ver2 60.8954324 seconds for 1 000 000 iterations
# ver3 17.8502226 seconds for 1 000 000 iterations
# ver4 4.67465290 seconds for 1 000 000 iterations
