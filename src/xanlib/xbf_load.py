from os import PathLike
from xanlib.scene import Scene


def load_xbf(filename: str | PathLike) -> Scene:
    with open(filename, "rb") as stream:
        buffer = stream.read()

    last_byte = int.from_bytes(buffer[-4:], "little", signed=True)
    assert last_byte == -1, f"Expected EOF, got {last_byte}"
    return Scene.frombuffer(buffer[:-4])
