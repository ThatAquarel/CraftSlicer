# CraftSlicer

<p>
<a href="https://github.com/badges/shields/graphs/contributors">
        <img src="https://img.shields.io/badge/version-2.0-brightgreen" alt="version 2.0"/>
        <img src="https://img.shields.io/github/license/ThatAquarel/CraftSlicer" alt="licence MIT"/>
</a>
</p>
CraftSlicer is a pure python application to import 3D objects into your Minecraft world. Models and scans in the .stl
format can be converted into blocks, and then colored using reference images. At the press of a button, they can open in
your game directly, or be converted into a format compatible with
the [Litematica mod](https://github.com/maruohon/litematic).

## Demo

Insert video here

## Installation

The current version (2.0) only supports MS Windows, though macOS and Linux distributions will be in the future.

#### Windows

Download the latest Python interpreter (version 3.9.x) via the [Python website](https://www.python.org/downloads/).
During the installation process, make sure to check the option `Add Python 3.9.x to PATH`. To install and open
CraftSlicer, run the following commands in a command prompt:

```shell
py -3.9 -m pip install CraftSlicer
py -3.9 -m craftslicer
```

For the converted models to open directly in your world, download
the [CraftSlicer Litematica mod](https://github.com/ThatAquarel/litematica/releases/). Then place the .jar file in the
Minecraft mods folder, located by default at `%appdata%/.minecraft/mods/`. Note that this is only
a [Fabric](https://fabricmc.net/) mod for 1.16.4 and 1.16.5.

## Documentation

If you are unsure about the usage of CraftSlicer after installing, refer to these links:

|Index          |Link                                                                                              |
|---------------|--------------------------------------------------------------------------------------------------|
|App user manual| [CraftSlicer/doc/MANUAL.md](https://github.com/ThatAquarel/CraftSlicer/blob/master/doc/MANUAL.md)|
|Api usage      | [CraftSlicer/doc/API.md](https://github.com/ThatAquarel/CraftSlicer/blob/master/doc/API.md)      |
