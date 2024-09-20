import pytest
import json
import binascii
from xanlib.scene import (
    Vertex,
    Face,
    VertexAnimation
)


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
def vertex_data(request):
    data = request.param
    encoded_position = binascii.unhexlify(data['encoded']['position'])
    encoded_normal = binascii.unhexlify(data['encoded']['normal'])
    encoded = encoded_position + encoded_normal

    decoded = Vertex(
        position=tuple(data['decoded']['position']),
        normal=tuple(data['decoded']['normal'])
    )

    return encoded, decoded

@pytest.fixture(params=load_test_data('tests/test_data/faces.json'))
def face_data(request):
    data = request.param
    attrs = ['vertex_indices', 'texture_index', 'flags', 'uv_coords']
    encoded = b''.join([binascii.unhexlify(data['encoded'][attr]) for attr in attrs])

    decoded = Face(
        tuple(data['decoded']['vertex_indices']),
        data['decoded']['texture_index'],
        data['decoded']['flags'],
        tuple(tuple(uv) for uv in data['decoded']['uv_coords'])
    )

    return encoded, decoded


@pytest.fixture
def vertex_animation():

    vertex_animations = []

    # Binary data for frame_count (2), count (1), actual (3)
    frame_count_bin = b'\x02\x00\x00\x00'  # 2 as int
    count_bin = b'\x01\x00\x00\x00'        # 1 as int
    actual_bin = b'\x03\x00\x00\x00'       # 3 as int

    # Binary data for key_list: 3 unsigned integers (1, 2, 3)
    key_list_bin = (
        b'\x01\x00\x00\x00'  # 1
        b'\x02\x00\x00\x00'  # 2
        b'\x03\x00\x00\x00'  # 3
    )

    binary_data = frame_count_bin + count_bin + actual_bin + key_list_bin

    decoded = VertexAnimation(
        frame_count=2,
        count=1,
        actual=3,
        keys=[1, 2, 3],
        scale=None,
        base_count=None,
        real_count=None,
        body=None,
        interpolation_data=None
    )

    vertex_animations.append({
            'binary': binary_data,
            'decoded': decoded
        })

    for va in vertex_animations:
        yield va
