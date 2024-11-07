from os import PathLike
from xanlib.scene import Scene


def load_xbf(filename: str | PathLike) -> Scene:
    with open(filename, "rb") as f:
        return Scene.fromstream(f)
