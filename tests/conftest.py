import pytest
from xanlib.scene import VertexAnimation


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


@pytest.fixture
def pos_int():
    yield {
            'binary': b'\x40\xe2\x01\x00',
            'decoded': 123456
        }

@pytest.fixture
def vertex_animation():
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

    yield {
            'binary': binary_data,
            'decoded': decoded
        }
