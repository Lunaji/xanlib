from os import PathLike
from xanlib.scene import Scene


def save_xbf(scene: Scene, filename: str | PathLike) -> None:
    with open(filename, "wb") as f:
        f.write(bytes(scene))
