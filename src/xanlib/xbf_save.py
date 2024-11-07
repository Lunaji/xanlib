from os import PathLike
from struct import pack, Struct
from xanlib.scene import Scene


def save_xbf(scene: Scene, filename: str | PathLike) -> None:
    with open(filename, "wb") as f:
        header_fmt = Struct(f"<2i{len(scene.FXData)}si{len(scene.textureNameData)}s")
        f.write(
            header_fmt.pack(
                scene.version,
                len(scene.FXData),
                scene.FXData,
                len(scene.textureNameData),
                scene.textureNameData,
            )
        )
        for node in scene.nodes:
            f.write(bytes(node))
        if scene.unparsed is not None:
            f.write(scene.unparsed)
        else:
            f.write(pack("i", -1))
