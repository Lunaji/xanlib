import io
import pytest
from xanlib.xbf_save import (
    write_Int32sl,
    write_vertex,
    write_vertex_animation,
)

@pytest.fixture()
def buffer():
    return io.BytesIO()

def test_write_Int32sl(buffer, pos_int):
    write_Int32sl(buffer, pos_int['decoded'])
    assert buffer.getvalue() == pos_int['binary']

def test_write_vetex(buffer, vertex_data):
    expected, given = vertex_data
    write_vertex(buffer, given)
    assert buffer.getvalue() == expected

def test_write_vertex_animation(buffer, vertex_animation):
    write_vertex_animation(buffer, vertex_animation['decoded'])
    assert buffer.getvalue() == vertex_animation['binary']

