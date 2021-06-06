from distutils.core import setup

# noinspection PyUnresolvedReferences
import py2exe

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
    ("platforms", ["C:\\Users\\xia_t\\anaconda3\\envs\\CraftSlicer\\Lib\\site-packages"
                   "\\PyQt5\\Qt5\\plugins\\platforms\\qwindows.dll"]),
    ("", [r"c:\windows\syswow64\MSVCP100.dll", r"c:\windows\syswow64\MSVCR100.dll"])
]

requirements = open("requirements.txt", "r").read().split("\\n")

setup(
    name='CraftSlicer',
    version='0.1',
    console=[{'script': "craftslicer_v2.py"}],
    # url='',
    # license='',
    data_files=datafiles,
    options={
        "py2exe": {
            "includes": includes,
            "excludes": ["OpenGL"],
        }
    }
)
