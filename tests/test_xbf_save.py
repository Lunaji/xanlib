import io
import pytest
from xanlib.xbf_save import (
    write_Int32sl,
    write_vertex,
    write_face,
    write_vertex_animation,
    write_key_animation,
    write_node,
)

@pytest.fixture()
def buffer():
    return io.BytesIO()

def test_write_Int32sl(buffer, pos_int):
    write_Int32sl(buffer, pos_int['decoded'])
    assert buffer.getvalue() == pos_int['binary']

def test_write_vertex(buffer, vertex):
    write_vertex(buffer, vertex.decoded)
    assert buffer.getvalue() == vertex.encoded

def test_write_face(buffer, face):
    write_face(buffer, face.decoded)
    assert buffer.getvalue() == face.encoded

def test_write_vertex_animation(buffer, vertex_animation):
    write_vertex_animation(buffer, vertex_animation.decoded)
    assert buffer.getvalue() == vertex_animation.encoded

def test_write_key_animation(buffer, key_animation):
    write_key_animation(buffer, key_animation.decoded)
    assert buffer.getvalue() == key_animation.encoded

def test_write_node_basic(buffer, node_basic):
    write_node(buffer, node_basic.decoded)
    assert buffer.getvalue() == node_basic.encoded
