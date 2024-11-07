from os import PathLike
from struct import unpack, calcsize
from xanlib.node import Node
from xanlib.scene import Scene


def load_xbf(filename: str | PathLike) -> Scene:
    scene = Scene(file=filename)
    with open(filename, "rb") as f:
        header_fmt = "<2i"
        header_size = calcsize(header_fmt)
        scene.version, fxdata_size = unpack(header_fmt, f.read(header_size))
        scene.FXData = f.read(fxdata_size)
        texture_data_size = unpack("<i", f.read(4))[0]
        scene.textureNameData = f.read(texture_data_size)
        while True:
            try:
                node = Node.fromstream(f)
                if node.transform is None:
                    current_position = f.tell()
                    f.seek(0, 2)
                    assert current_position == f.tell(), "Not at EOF"
                    return scene
                scene.nodes.append(node)
            except Exception as e:
                scene.error = e
                scene.unparsed = f.read()
                return scene
