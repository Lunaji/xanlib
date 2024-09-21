import pytest
import json
import binascii
from collections import namedtuple
from xanlib.scene import (
    Vertex,
    Face,
    VertexAnimation
)

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
        position=tuple(data['decoded']['position']),
        normal=tuple(data['decoded']['normal'])
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
        tuple(tuple(uv) for uv in data['decoded']['uv_coords'])
    )

    yield EncodedDecoded(encoded, decoded)


@pytest.fixture(params=load_test_data('tests/test_data/vertex_animations.json'))
def vertex_animation(request):
    data = request.param

    encoded = binascii.unhexlify(data['encoded'])
    decoded = VertexAnimation(
                frame_count=data['decoded']['frame_count'],
                count=data['decoded']['count'],
                actual=data['decoded']['actual'],
                keys=data['decoded']['keys'],
                scale=data['decoded']['scale'],
                base_count=data['decoded']['base_count'],
                real_count=data['decoded']['real_count'],
                body=data['decoded']['body'],
                interpolation_data=data['decoded']['interpolation_data'],
              )

    yield EncodedDecoded(encoded, decoded)
