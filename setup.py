import pathlib
import craftslicer
from setuptools import setup, find_packages

directory = pathlib.Path(__file__).parent
readme = (directory / "README.md").read_text()
requirements = [i.replace("\n", "") for i in open("requirements.txt", "r").readlines()]

setup(
    name="CraftSlicer",
    version=craftslicer.__version__,
    description="A portal from reality to Minecraft",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/ThatAquarel/CraftSlicer",
    author="Aquarel",
    author_email="flyingrobot910@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment"
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "craftslicer=craftslicer.__main__:main",
        ]
    }
)
