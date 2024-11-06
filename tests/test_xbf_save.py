import io
import pytest
from xanlib.xbf_save import (
    write_key_animation,
    write_node,
    save_xbf,
)


@pytest.fixture()
def stream():
    return io.BytesIO()


def test_write_vertex(vertex):
    assert bytes(vertex.decoded) == vertex.encoded


def test_write_face(stream, face):
    assert bytes(face.decoded) == face.encoded


def test_write_vertex_animation(stream, vertex_animation):
    assert bytes(vertex_animation.decoded) == vertex_animation.encoded


def test_write_key_animation(stream, key_animation):
    write_key_animation(stream, key_animation.decoded)
    assert stream.getvalue() == key_animation.encoded


def test_write_node_basic(stream, node_basic):
    write_node(stream, node_basic.decoded)
    assert stream.getvalue() == node_basic.encoded


def test_write_node_with_children(stream, node_with_children):
    node_with_children.decoded.children[0].parent = None  # TODO: remove this line
    write_node(stream, node_with_children.decoded)
    assert stream.getvalue() == node_with_children.encoded


def test_save_xbf(mocker, scene):
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    save_xbf(scene.decoded, scene.decoded.file)
    mock_open.assert_called_once_with(scene.decoded.file, "wb")
