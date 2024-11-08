from os import PathLike
from xanlib.scene import Scene


def load_xbf(filename: str | PathLike) -> Scene:
    with open(filename, "rb") as stream:
        buffer = stream.read()
    return Scene.frombuffer(buffer)
