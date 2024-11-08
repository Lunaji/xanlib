from os import PathLike
from xanlib.scene import Scene


def load_xbf(filename: str | PathLike) -> Scene:
    with open(filename, "rb") as stream:
        buffer = stream.read()

    last_int = int.from_bytes(buffer[-4:], "little", signed=True)
    assert last_int == -1, f"Expected EOF, got {last_int}"
    return Scene.frombuffer(buffer[:-4])


def save_xbf(scene: Scene, filename: str | PathLike) -> None:
    buffer = bytes(scene)

    if scene.unparsed is None:
        buffer += (-1).to_bytes(4, "little", signed=True)

    with open(filename, "wb") as stream:
        stream.write(buffer)
