import pytest
import json
import binascii
from pathlib import Path
from collections import namedtuple
from xanlib.vertex import Vertex
from xanlib.face import Face
from xanlib.compressed_vertex import CompressedVertex
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation
from xanlib.node import Node
from xanlib.scene import Scene

EncodedDecoded = namedtuple("EncodedDecoded", ["encoded", "decoded"])


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(
    params=[
        (0, 0),  # 0 should stay 0
        (15, 15),  # Maximum positive value
        (16, 0),  # 16 should map to -0 (considered 0)
        (31, -15),  # 31 should be -15 (max negative)
        (32, 0),  # Wrapped around, should behave like 0
        (47, 15),  # Wrapped, behaves like 15
        (1, 1),  # Simple positive test
        (17, -1),  # Corresponding negative test
        (5, 5),  # Another positive test
        (21, -5),  # Corresponding negative test
    ]
)
def signed_5bit(request):
    yield request.param


def load_test_data(json_file):
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_path = test_data_dir / json_file
    with test_data_path.open("r") as file:
        return json.load(file)


def prepare_vertex(data):
    encoded_position = binascii.unhexlify(data["encoded"]["position"])
    encoded_normal = binascii.unhexlify(data["encoded"]["normal"])
    encoded = encoded_position + encoded_normal

    decoded = Vertex(*data["decoded"]["position"], *data["decoded"]["normal"])

    return EncodedDecoded(encoded, decoded)


@pytest.fixture(params=load_test_data("vertices.json"))
def vertex(request):
    yield prepare_vertex(request.param)


@pytest.fixture(params=load_test_data("faces.json"))
def face(request):
    data = request.param
    attrs = ["vertex_indices", "texture_index", "flags", "uv_coords"]
    encoded = b"".join([binascii.unhexlify(data["encoded"][attr]) for attr in attrs])

    uv_coords = [coord for uv in data["decoded"]["uv_coords"] for coord in uv]

    decoded = Face(
        *data["decoded"]["vertex_indices"],
        data["decoded"]["texture_index"],
        data["decoded"]["flags"],
        *uv_coords,
    )

    yield EncodedDecoded(encoded, decoded)


@pytest.fixture(params=load_test_data("vertex_animations.json"))
def vertex_animation(request):
    data = request.param
    yield EncodedDecoded(
        binascii.unhexlify(data["encoded"]),
        VertexAnimation(
            frame_count=data["decoded"]["frame_count"],
            count=data["decoded"]["count"],
            keys=data["decoded"]["keys"],
            scale=data["decoded"]["scale"],
            base_count=data["decoded"]["base_count"],
            real_count=data["decoded"]["real_count"],
            frames=(
                [
                    [CompressedVertex(*datum) for datum in frame]
                    for frame in data["decoded"]["frames"]
                ]
                if data["decoded"]["frames"] is not None
                else []
            ),
            interpolation_data=(
                data["decoded"]["interpolation_data"]
                if data["decoded"]["interpolation_data"] is not None
                else []
            ),
        ),
    )


@pytest.fixture(params=load_test_data("key_animations.json"))
def key_animation(request):
    data = request.param

    encoded = binascii.unhexlify(data["encoded"])
    decoded = KeyAnimation(
        frame_count=data["decoded"]["frame_count"],
        flags=data["decoded"]["flags"],
        matrices=[tuple(matrix) for matrix in data["decoded"]["matrices"]],
        extra_data=data["decoded"]["extra_data"] or [],
        frames=data["decoded"].get("frames", None) or [],
    )

    yield EncodedDecoded(encoded, decoded)


@pytest.fixture
def matrix():
    decoded = (0.0,) * 16
    encoded = b"\x00" * (8 * 16)
    yield EncodedDecoded(encoded, decoded)


@pytest.fixture
def node_basic(face, matrix):
    face_bin, expected_face = face

    vertex_data = load_test_data("vertices.json")
    vertices_prepared = [prepare_vertex(data) for data in vertex_data]
    vertices_encoded = b"".join([vertex.encoded for vertex in vertices_prepared])
    vertices_decoded = [vertex.decoded for vertex in vertices_prepared]

    vertexCount_bin = len(vertices_prepared).to_bytes(4, "little")
    flags_bin = b"\x01\x00\x00\x00"  # NodeFlags.PRELIGHT (1)
    faceCount_bin = b"\x01\x00\x00\x00"  # 1 as int
    childCount_bin = b"\x00\x00\x00\x00"  # 0 as int (no children)

    # Name: length = 8, "TestNode"
    nameLength_bin = b"\x08\x00\x00\x00"  # 8 as int
    name_bin = b"TestNode"

    rgb_bin = b"\xff\x00\x00\xff\xff\xff"

    binary_data = (
        vertexCount_bin
        + flags_bin
        + faceCount_bin
        + childCount_bin
        + matrix.encoded
        + nameLength_bin
        + name_bin
        + vertices_encoded
        + face_bin
        + rgb_bin
    )

    decoded = Node(
        transform=matrix.decoded,
        name="TestNode",
        vertices=vertices_decoded,
        faces=[expected_face],
        rgb=[(255, 0, 0), (255, 255, 255)],
    )

    yield EncodedDecoded(binary_data, decoded)


@pytest.fixture
def node_with_children(vertex, face, matrix, node_basic):
    vertex_bin, expected_vertex = vertex
    face_bin, expected_face = face

    # Binary data for parent node (vertexCount = 1, faceCount = 1, childCount = 1)
    vertexCount_bin = b"\x01\x00\x00\x00"  # 1 as int
    flags_bin = b"\x01\x00\x00\x00"  # NodeFlags.PRELIGHT (1)
    faceCount_bin = b"\x01\x00\x00\x00"  # 1 as int
    childCount_bin = b"\x01\x00\x00\x00"  # 1 as int (1 child)

    # Name: length = 10, "ParentNode"
    nameLength_bin = b"\x0a\x00\x00\x00"  # 10 as int
    parent_name_bin = b"ParentNode"

    # RGB color data for parent vertex: (255, 0, 0)
    rgb_bin = b"\xff\x00\x00"

    encoded = (
        vertexCount_bin
        + flags_bin
        + faceCount_bin
        + childCount_bin
        + matrix.encoded
        + nameLength_bin
        + parent_name_bin
        + node_basic.encoded
        + vertex_bin
        + face_bin
        + rgb_bin
    )

    decoded = Node(
        transform=matrix.decoded,
        name="ParentNode",
        vertices=[expected_vertex],
        faces=[expected_face],
        rgb=[(255, 0, 0)],
        children=[node_basic.decoded],
    )

    yield EncodedDecoded(encoded, decoded)


@pytest.fixture
def scene(node_basic):
    version = 1
    FXData = b"FXDataHeader"
    textureNameData = b"foobar.tga\x00\x00"
    nodes = [node_basic.decoded]

    encoded = (
        version.to_bytes(4, "little")
        + len(FXData).to_bytes(4, "little")
        + FXData
        + len(textureNameData).to_bytes(4, "little")
        + textureNameData
        + node_basic.encoded
    )

    decoded = Scene(
        version=version,
        FXData=FXData,
        textureNameData=textureNameData,
        nodes=nodes,
    )

    yield EncodedDecoded(encoded, decoded)
