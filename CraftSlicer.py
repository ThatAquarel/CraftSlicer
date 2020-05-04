import trimesh
import numpy as np
import sys
import time
import os
import shutil
from time import gmtime, strftime
from os import listdir, path
from os.path import isfile, join
from nbt import *
from PIL import Image, ImageChops, ImageOps

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '='):
    iteration += 1
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s [%s] %s%% %s' % (prefix, bar, percent, suffix), end = "\r")
    if iteration == total:
        print()

def deleteFolder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def rotateArray(array, n):
    return array[n:] + array[:n]

def genTextures(image, side, horizontalSize):
    global finalTextures

    textureChunks = []
    for i in range(zSize + 1):
        for j in range(horizontalSize + 1):
            image.crop((i * 16, j * 16, (i + 1) * 16, (j + 1) * 16)).save("./temp_img/" + str(i) + "_" + str(j) + ".png")
            textureChunks.append(str(i) + "_" + str(j) + ".png")
        printProgressBar(i, zSize + 1, "[INFO] Fitting "+ side + " side textures.")

    assets = open("textures.txt", "r").readlines()

    for i in textureChunks:
        img1 = Image.open("./temp_img/" + i)
        img1 = np.asarray(img1)
        closestTexture = [765, "", 0, 0]
        r1 = []
        g1 = []
        b1 = []
        for j in range(len(img1)):
            for k in range(len(img1[j])):
                r1.append(img1[j][k][0])
                g1.append(img1[j][k][1])
                b1.append(img1[j][k][2])
        img1Average = [int(round(np.average(r1))), int(round(np.average(g1))), int(round(np.average(b1)))]

        for j in assets:
            img2Average = [int(j.replace("\n", "").split(" ")[3]), int(j.replace("\n", "").split(" ")[4]),
                           int(j.replace("\n", "").split(" ")[5])]
            difference = [0, 0, 0]
            for k in range(3):
                difference[k] = img1Average[k] - img2Average[k]
                if difference[k] < 0:
                    difference[k] *= -1
            differenceTotal = difference[0] + difference[1] + difference[2]
            if differenceTotal < closestTexture[0]:
                closestTexture[0] = differenceTotal
                closestTexture[1] = j
                closestTexture[2] = j.replace("\n", "").split(" ")[1]
                closestTexture[3] = j.replace("\n", "").split(" ")[2]
        currentIndex = 0
        for j in range(len(textureChunks)):
            if textureChunks[j] == i:
                currentIndex = j
        finalTextures.append(closestTexture)
        printProgressBar(currentIndex, len(textureChunks), "[INFO] Generating " + side + " side textures.")

def incorrectArgs():
    print("[ERROR] Required arguements:")
    print("[ERROR] Arg1 ==>> Target mesh directory(.stl).")
    print("[ERROR] Arg2 ==>> Target mesh north side texture directory(.png).")
    print("[ERROR] Arg3 ==>> Target mesh south side texture directory(.png).")
    print("[ERROR] Arg4 ==>> Target mesh east side texture directory(.png).")
    print("[ERROR] Arg5 ==>> Target mesh west side texture directory(.png).")
    exit()

millisecondStart = int(round(time.time() * 1000))

if len(sys.argv) != 6:
    print("[ERROR] Invalid arguments.")
    incorrectArgs()

for i in sys.argv:
    if not path.exists(i):
        print("[ERROR] No such file or directory \"" + i + "\".")
        incorrectArgs()

printProgressBar(0, 1, "[INFO] Loading mesh.")
mesh0 = trimesh.load_mesh(str(sys.argv[1]))
trimesh.repair.fill_holes(mesh0)
mesh0.units = "mm"
mesh0 = trimesh.remesh.subdivide_to_size(max_edge=0.5,vertices=mesh0.vertices,faces=mesh0.faces)
mesh0 = trimesh.Trimesh(vertices=mesh0[0],faces=mesh0[1],process=False)

printProgressBar(0, 1, "[INFO] Slicing mesh.")
zStep = 1.0
zExtents = mesh0.bounds[:,2]
zLevels  = np.arange(*zExtents, step=zStep)
sectionsZ = mesh0.section_multiplane(plane_origin=mesh0.bounds[0],plane_normal=[0,0,1],heights=zLevels)

filenames = []
sectionsZ = [i for i in sectionsZ if i]
for i in range(len(sectionsZ)):
    sectionsZ[i] = sectionsZ[i].extrude(zStep).export("./temp/" + str(i) + ".stl")
    filenames.append("./temp/" + str(i) + ".stl")
    printProgressBar(i, len(sectionsZ), "[INFO] Reloading meshes.")

mesh1 = []
for i in range(len(filenames)):
    mesh1.append(None)
    mesh1[i] = trimesh.load_mesh(filenames[i])
    printProgressBar(i, len(sectionsZ), "[INFO] Generating vertices.")
mesh2 = []
for i in range(len(mesh1)):
    mesh1[i] = mesh1[i].section(plane_origin=mesh1[0].centroid, plane_normal=[0,0,1])
    mesh2.append(None)
    mesh2[i], to_3D = mesh1[i].to_planar()
    mesh2[i] = mesh2[i].vertices

xValues = []
yValues = []
for i in range(len(mesh2)):
    for j in range(len(mesh2[i])):
        xValues.append(mesh2[i][j][0])
        yValues.append(mesh2[i][j][1])
xMinVal = min(xValues) * -1
yMinVal = min(yValues) * -1
xValues += xMinVal
yValues += yMinVal
xSize = int(round(max(xValues), 0))
ySize = int(round(max(yValues), 0))
zSize = int(len(filenames))

blocks = [[[0 for k in range(ySize + 1)] for j in range(xSize + 1)] for i in range(zSize + 1)]
data = [[[0 for k in range(ySize + 1)] for j in range(xSize + 1)] for i in range(zSize + 1)]

for i in range(len(mesh2)):
    for j in range(len(mesh2[i])):
        mesh2[i][j][0] += xMinVal
        mesh2[i][j][1] += yMinVal
    printProgressBar(i, len(mesh2), "[INFO] Creating arrays.")

for i in range(len(mesh2)):
    for j in range(len(mesh2[i])):
        for k in range(len(blocks[i])):
            if k <= mesh2[i][j][0] < k + 1:
                for l in range(len(blocks[i][k])):
                    if l <= mesh2[i][j][1] < l + 1:
                        blocks[i][k][l] = 1
    printProgressBar(i, len(mesh2), "[INFO] Writing vertices to arrays.")

if str(sys.argv[2]) != "None":
    finalTextures = []
    im = Image.open(str(sys.argv[2]))
    im = im.transpose(Image.ROTATE_270)
    im = im.resize(((zSize + 1) * 16, (ySize + 1) * 16))
    genTextures(im, "north", ySize)
    finalTextures = rotateArray(finalTextures, ySize)
    for i in range(len(blocks)):
        for j in range(len(blocks[i][0])):
            for k in range(len(blocks[i])):
                if blocks[i][k][j] == 1:
                    blocks[i][k][j] = int(finalTextures[i * (ySize + 1) - j][2])
                    data[i][k][j] = int(finalTextures[i * (ySize + 1) - j][3])
                    break
        printProgressBar(i, len(blocks), "[INFO] Writing north side textures to arrays.")

if str(sys.argv[3]) != "None":
    finalTextures = []
    im = Image.open(str(sys.argv[3]))
    im = ImageOps.mirror(im)
    im = im.transpose(Image.ROTATE_270)
    im = im.resize(((zSize + 1) * 16, (ySize + 1) * 16))
    genTextures(im, "south", ySize)
    finalTextures = rotateArray(finalTextures, ySize)
    for i in range(len(blocks)):
        for j in range(len(blocks[i][0])):
            for k in range(len(blocks[i])):
                k = len(blocks[i]) - k - 1
                if blocks[i][k][j] == 1:
                    blocks[i][k][j] = int(finalTextures[i * (ySize + 1) - j][2])
                    data[i][k][j] = int(finalTextures[i * (ySize + 1) - j][3])
                    break
        printProgressBar(i, len(blocks), "[INFO] Writing south side textures to arrays.")

if str(sys.argv[4]) != "None":
    finalTextures = []
    im = Image.open(str(sys.argv[4]))
    im = im.transpose(Image.ROTATE_270)
    im = im.resize(((zSize + 1) * 16, (xSize + 1) * 16))
    genTextures(im, "east", xSize)
    finalTextures = rotateArray(finalTextures, xSize)
    for i in range(len(blocks)):
        for j in range(len(blocks[i])):
            for k in range(len(blocks[i][j])):
                k = len(blocks[i][j]) - k - 1
                if blocks[i][j][k] == 1:
                    blocks[i][j][k] = int(finalTextures[i * (xSize + 1) - j][2])
                    data[i][j][k] = int(finalTextures[i * (xSize + 1) - j][3])
                    break
        printProgressBar(i, len(blocks), "[INFO] Writing east side textures to arrays.")

if str(sys.argv[5]) != "None":
    finalTextures = []
    im = Image.open(str(sys.argv[5]))
    im = ImageOps.mirror(im)
    im = im.transpose(Image.ROTATE_270)
    im = im.resize(((zSize + 1) * 16, (xSize + 1) * 16))
    genTextures(im, "west", xSize)
    finalTextures = rotateArray(finalTextures, xSize)
    for i in range(len(blocks)):
        for j in range(len(blocks[i])):
            for k in range(len(blocks[i][j])):
                if blocks[i][j][k] == 1:
                    blocks[i][j][k] = int(finalTextures[i * (xSize + 1) - j][2])
                    data[i][j][k] = int(finalTextures[i * (xSize + 1) - j][3])
                    break
        printProgressBar(i, len(blocks), "[INFO] Writing west side textures to arrays.")

#for i in range(len(blocks)):
#    print("\n")
#    for j in range(len(blocks[i])):
#        print(blocks[i][j])

nbtfile = nbt.NBTFile()
nbtfile.name = "Schematic"
entities = nbt.TAG_List(name="Entities", type=nbt.TAG_Long)
tileEntities = nbt.TAG_List(name="TileEntities", type=nbt.TAG_Long)
nbtfile.tags.append(entities)
nbtfile.tags.append(tileEntities)

nbtfile.tags.append(nbt.TAG_Short(name="Height", value=zSize + 1))
nbtfile.tags.append(nbt.TAG_Short(name="Length", value=xSize + 1))
nbtfile.tags.append(nbt.TAG_Short(name="Width", value=ySize + 1))

nbtfile.tags.append(nbt.TAG_String(name="Materials", value="Alpha"))

nbtfile.tags.append(nbt.TAG_Int(name="WEOffsetX", value=0))
nbtfile.tags.append(nbt.TAG_Int(name="WEOffsetY", value=0))
nbtfile.tags.append(nbt.TAG_Int(name="WEOffsetZ", value=0))
nbtfile.tags.append(nbt.TAG_Int(name="WEOriginX", value=0))
nbtfile.tags.append(nbt.TAG_Int(name="WEOriginY", value=0))
nbtfile.tags.append(nbt.TAG_Int(name="WEOriginZ", value=0))

finalBlocks = []
for i in range(len(blocks)):
    for j in range(len(blocks[i])):
        for k in range(len(blocks[i][j])):
            finalBlocks.append(blocks[i][j][k])
    printProgressBar(i, len(blocks), "[INFO] Writing blocks to file.")
blocksNbt = nbt.TAG_Byte_Array(name="Blocks")
blocksNbt.value = bytearray(finalBlocks)
nbtfile.tags.append(blocksNbt)

finalData = []
for i in range(len(data)):
    for j in range(len(data[i])):
        for k in range(len(data[i][j])):
            finalData.append(data[i][j][k])
    printProgressBar(i, len(blocks), "[INFO] Writing block data to file.")
dataNbt = nbt.TAG_Byte_Array(name="Data")
dataNbt.value = bytearray(finalData)
nbtfile.tags.append(dataNbt)

#print("[DEBUG] Data written to file: \n" + nbtfile.pretty_tree())

nbtfile.write_file(str(os.path.basename(sys.argv[1])).split(".")[0] + ".schematic")
millisecondTotal = int(round(time.time() * 1000)) - millisecondStart
print("[INFO] Took " + str(millisecondTotal) + " milliseconds(" + str(millisecondTotal / 1000) + " seconds) to complete.")
print("[INFO] File saved as: " + str(os.path.basename(sys.argv[1])).split(".")[0] + ".schematic.")

print("[INFO] Deleting temp files")
deleteFolder("./temp/")
deleteFolder("./temp_img/")