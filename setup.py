import os
from os.path import expanduser
import shutil
from distutils.core import setup

# noinspection PyUnresolvedReferences
import py2exe


def delete_dir(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except OSError:
            pass


def copy_dir(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


includes = [
    "PyQt5.sip",
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "numpy",
    "pyrr",
    "PIL",
    "trimesh",
    "nbt",
    "qdarkstyle",
    "core",
    "ctypes",
    "logging"
]

datafiles = [
    ("platforms", [expanduser(
        "~\\anaconda3\\envs\\CraftSlicer\\Lib\\site-packages\\PyQt5\\Qt5\\plugins\\platforms\\qwindows.dll")]),
    ("", [r"C:\windows\syswow64\MSVCP100.dll", r"C:\windows\syswow64\MSVCR100.dll"])
]

dist_path = os.path.join(os.path.dirname(__file__), ".\\dist\\")

delete_dir(dist_path)
setup(
    name="CraftSlicer",
    version="0.1",
    console=[{"script": "craftslicer_v2.py"}],
    data_files=datafiles,
    options={
        "py2exe": {
            "includes": includes,
            "excludes": ["OpenGL"],
        }
    }
)

opengl_path = os.path.join(dist_path, ".\\OpenGL\\")
os.mkdir(opengl_path)
copy_dir(expanduser("~\\anaconda3\\envs\\CraftSlicer\\Lib\\site-packages\\OpenGL\\"), opengl_path)
