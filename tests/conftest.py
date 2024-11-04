import pytest
import json
import binascii
from collections import namedtuple
from xanlib.math_utils import Vector3, UV
from xanlib.vertex import Vertex
from xanlib.face import Face
from xanlib.compressed_vertex import CompressedVertex
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation
from xanlib.node import Node, NodeFlags
from xanlib.scene import Scene

EncodedDecoded = namedtuple('EncodedDecoded', ['encoded', 'decoded'])

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


@pytest.fixture(params=[
    (0, 0),    # 0 should stay 0
    (15, 15),  # Maximum positive value
    (16, 0),   # 16 should map to -0 (considered 0)
    (31, -15), # 31 should be -15 (max negative)
    (32, 0),   # Wrapped around, should behave like 0
    (47, 15),  # Wrapped, behaves like 15
    (1, 1),    # Simple positive test
    (17, -1),  # Corresponding negative test
    (5, 5),    # Another positive test
    (21, -5),  # Corresponding negative test
])
def signed_5bit(request):
    yield request.param

@pytest.fixture
def pos_int():
    yield {
            'binary': b'\x40\xe2\x01\x00',
            'decoded': 123456
        }

def load_test_data(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)

@pytest.fixture(params=load_test_data('tests/test_data/vertices.json'))
def vertex(request):
    data = request.param
    encoded_position = binascii.unhexlify(data['encoded']['position'])
    encoded_normal = binascii.unhexlify(data['encoded']['normal'])
    encoded = encoded_position + encoded_normal

    decoded = Vertex(
        position=Vector3(*data['decoded']['position']),
        normal=Vector3(*data['decoded']['normal'])
    )

    yield EncodedDecoded(encoded, decoded)

@pytest.fixture(params=load_test_data('tests/test_data/faces.json'))
def face(request):
    data = request.param
    attrs = ['vertex_indices', 'texture_index', 'flags', 'uv_coords']
    encoded = b''.join([binascii.unhexlify(data['encoded'][attr]) for attr in attrs])

    decoded = Face(
        tuple(data['decoded']['vertex_indices']),
        data['decoded']['texture_index'],
        data['decoded']['flags'],
        tuple(UV(*uv) for uv in data['decoded']['uv_coords'])
    )

    yield EncodedDecoded(encoded, decoded)


@pytest.fixture(params=load_test_data('tests/test_data/vertex_animations.json'))
def vertex_animation(request):
    data = request.param
    yield EncodedDecoded(
                            binascii.unhexlify(data['encoded']),
                            VertexAnimation(
                                            frame_count=data['decoded']['frame_count'],
                                            count=data['decoded']['count'],
                                            actual=data['decoded']['actual'],
                                            keys=data['decoded']['keys'],
                                            scale=data['decoded']['scale'],
                                            base_count=data['decoded']['base_count'],
                                            real_count=data['decoded']['real_count'],
                                            frames=[[CompressedVertex(*datum) for datum in frame] for frame in data['decoded']['frames']]if data['decoded']['frames'] is not None else None,
                                            interpolation_data=data['decoded']['interpolation_data'],
                                        )
                        )

@pytest.fixture(params=load_test_data('tests/test_data/key_animations.json'))
def key_animation(request):
    data = request.param

    encoded = binascii.unhexlify(data['encoded'])
    decoded = KeyAnimation(
                frame_count=data['decoded']['frame_count'],
                flags=data['decoded']['flags'],
                matrices=[tuple(matrix) for matrix in data['decoded']['matrices']],
                actual=data['decoded']['actual'],
                extra_data=data['decoded']['extra_data'],
                frames=data['decoded'].get('frames', None)
              )

    yield EncodedDecoded(encoded, decoded)

@pytest.fixture
def matrix():
    decoded = (0.0,) * 16
    encoded = b'\x00' * (8 * 16)
    yield EncodedDecoded(encoded, decoded)

@pytest.fixture
def node_basic(vertex, face, matrix):
    vertex_bin, expected_vertex = vertex
    face_bin, expected_face = face

    # Binary data for vertexCount = 1, flags = NodeFlags.PRELIGHT, faceCount = 1, childCount = 0, name = "TestNode"
    vertexCount_bin = b'\x01\x00\x00\x00'  # 1 as int
    flags_bin = b'\x01\x00\x00\x00'  # NodeFlags.PRELIGHT (1)
    faceCount_bin = b'\x01\x00\x00\x00'  # 1 as int
    childCount_bin = b'\x00\x00\x00\x00'  # 0 as int (no children)

    # Name: length = 8, "TestNode"
    nameLength_bin = b'\x08\x00\x00\x00'  # 8 as int
    name_bin = b'TestNode'

    # RGB color data for 1 vertex: (255, 0, 0)
    rgb_bin = b'\xff\x00\x00'

    binary_data = (
            vertexCount_bin + flags_bin + faceCount_bin + childCount_bin +
            matrix.encoded + nameLength_bin + name_bin + vertex_bin + face_bin + rgb_bin
    )

    decoded = Node(
        flags= NodeFlags.PRELIGHT,
        transform= matrix.decoded,
        name= "TestNode",
        vertices= [expected_vertex],
        faces= [expected_face],
        rgb= [(255, 0, 0)]
    )

    yield EncodedDecoded(binary_data, decoded)

@pytest.fixture
def node_with_children(vertex, face, matrix):
    vertex_bin, expected_vertex = vertex
    face_bin, expected_face = face

    # Binary data for parent node (vertexCount = 1, faceCount = 1, childCount = 1)
    vertexCount_bin = b'\x01\x00\x00\x00'  # 1 as int
    flags_bin = b'\x01\x00\x00\x00'        # NodeFlags.PRELIGHT (1)
    faceCount_bin = b'\x01\x00\x00\x00'    # 1 as int
    childCount_bin = b'\x01\x00\x00\x00'   # 1 as int (1 child)

    # Name: length = 10, "ParentNode"
    nameLength_bin = b'\x0a\x00\x00\x00'  # 10 as int
    parent_name_bin = b'ParentNode'

    # RGB color data for parent vertex: (255, 0, 0)
    rgb_bin = b'\xff\x00\x00'

    # Binary data for child node (vertexCount = 1, faceCount = 1, childCount = 0)
    child_vertexCount_bin = b'\x01\x00\x00\x00'  # 1 as int
    child_flags_bin = b'\x01\x00\x00\x00'        # NodeFlags.PRELIGHT (1)
    child_faceCount_bin = b'\x01\x00\x00\x00'    # 1 as int
    child_childCount_bin = b'\x00\x00\x00\x00'   # 0 as int (no children)

    # Name: length = 9, "ChildNode"
    child_nameLength_bin = b'\x09\x00\x00\x00'  # 9 as int
    child_name_bin = b'ChildNode'

    # RGB color data for child vertex: (0, 255, 0)
    child_rgb_bin = b'\x00\xff\x00'

    child_node_bin = (
        child_vertexCount_bin + child_flags_bin + child_faceCount_bin + child_childCount_bin +
        matrix.encoded + child_nameLength_bin + child_name_bin + vertex_bin + face_bin + child_rgb_bin
    )

    encoded = (
        vertexCount_bin + flags_bin + faceCount_bin + childCount_bin +
        matrix.encoded + nameLength_bin + parent_name_bin + child_node_bin +
        vertex_bin + face_bin + rgb_bin
    )

    child = Node(
        flags= NodeFlags.PRELIGHT,
        transform= matrix.decoded,
        name= "ChildNode",
        vertices= [expected_vertex],
        faces= [expected_face],
        rgb= [(0, 255, 0)]
    )

    decoded = Node(
        flags= NodeFlags.PRELIGHT,
        transform= matrix.decoded,
        name= "ParentNode",
        vertices= [expected_vertex],
        faces= [expected_face],
        rgb= [(255, 0, 0)],
        children= [child]
    )

    yield EncodedDecoded(encoded, decoded)

@pytest.fixture
def scene(node_basic):
    file = 'foobar.xbf'
    version = 1
    FXData = b'FXDataHeader'
    textureNameData = b'foobar.tga\x00\x00'
    nodes = [node_basic.decoded]

    encoded = (
            version.to_bytes(4, 'little') +
            len(FXData).to_bytes(4, 'little') + FXData +
            len(textureNameData).to_bytes(4, 'little') + textureNameData +
            node_basic.encoded +
            (-1).to_bytes(4, 'little', signed=True) #EOF
            )

    decoded = Scene(
        version=version,
        FXData=FXData,
        textureNameData=textureNameData,
        nodes=nodes
    )

    yield EncodedDecoded(encoded, decoded)