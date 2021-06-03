import os


def full_path(file, rel_path=""):
    return os.path.join(os.path.dirname(file), rel_path)
