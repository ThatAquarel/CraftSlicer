# CraftSlicer
A slicer for Minecraft! Turn stl files into worledit schematic files using python 3.8.
Tested using Windows 10, Python 3.8 and Minecraft 1.12.2 with forge and worldedit. 

# Dependencies
- Trimesh, mesh manipulation library
- Numpy, array manipulation library
- Pillow, python imaging library
- Nbt, nbt modifiying library
- Os, system
- Sys, system
- Shutil, system
- Time, time library

# Running
Before running, create two folders, one named "temp" and the other "temp_img" in the same directory as CraftSlicer.py. These are required for the program to run.
The program requires 5 arguments:
- Target mesh directory(.stl).")
- Target mesh north side texture directory(.png).")
- Target mesh south side texture directory(.png).")
- Target mesh east side texture directory(.png).")
- Target mesh west side texture directory(.png).")

If there is no texture for one specific side, write "None".
Write all the arguments in the listed order.

# Examples
- py -3.8 CraftSlicer.py House.stl Side1.png Side2.png Side3.png Side4.png
- python CraftScliver.py Statue.stl Texture1.png None None Texture2.png
