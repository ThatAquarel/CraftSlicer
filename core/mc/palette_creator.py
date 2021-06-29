from pathlib import Path

import numpy as np
from PIL import Image

directory = "C:\\Users\\xia_t\\Desktop\\Main Folder\\minecraft\\assets\\minecraft\\"
blocks = [i.replace("\n", "") for i in open("one_dot_sixteen/one_dot_sixteen.txt", "r").readlines()]


def main():
    for block in blocks:
        mc_id, filename = block.split(",")

        paths = [path for path in Path(directory).rglob("%s*.png" % filename)]

        if len(paths) == 0:
            print("%s not found" % mc_id)
            continue

        image_average(paths[0].absolute(), mc_id)


def image_average(path, block):
    image = np.array(Image.open(path))

    if image.shape[-1] == 3:
        image = np.reshape(image, (-1, 3))
        alpha = np.repeat([255], image.shape[0])
        image = np.hstack((image, np.expand_dims(alpha, axis=1)))

    image = np.reshape(image, (-1, 4))

    alpha = image[:, 3]
    image = np.delete(image, 3, axis=1)

    average = np.round(np.average(image, axis=0, weights=alpha)).astype(int)

    print("\"minecraft:%s\": [%i, %i, %i]," % (block, average[0], average[1], average[2]))

    # if image.shape[-1] == 4:
    #     image = np.delete(image, 3, axis=2)
    #
    # image = np.reshape(image, (-1, 3))
    #
    # mean = np.mean(image, axis=0, dtype=int)
    # print("[\"minecraft:%s\",[%i,%i,%i]]" % (block, mean[0], mean[1], mean[2]))


if __name__ == '__main__':
    main()
