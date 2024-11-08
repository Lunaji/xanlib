from os import PathLike
from xanlib.scene import Scene


def save_xbf(scene: Scene, filename: str | PathLike) -> None:
    scene_buffer = bytes(scene)

    if scene.unparsed is None:
        scene_buffer += (-1).to_bytes(4, "little", signed=True)

    with open(filename, "wb") as f:
        f.write(scene_buffer)
